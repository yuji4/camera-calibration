import cv2
import numpy as np
import os
import sys
import argparse

CALIB_FILE   = "calibration_result.npz"
BOARD_COLS   = 7     # 내부 코너 가로 수
BOARD_ROWS   = 7        # 내부 코너 세로 수
SQUARE_SIZE  = 0.025    # 한 칸 실제 크기 (미터)
FRAME_SKIP   = 15       # 캘리브레이션 시 몇 프레임마다 추출할지
MIN_SAMPLES  = 20       # 캘리브레이션 최소 샘플 수


# Calibration
def run_calibration(video_path, preview=False):
    board_size = (BOARD_COLS, BOARD_ROWS)
    criteria   = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    obj_pt = np.zeros((BOARD_ROWS * BOARD_COLS, 3), np.float32)
    obj_pt[:, :2] = np.mgrid[0:BOARD_COLS, 0:BOARD_ROWS].T.reshape(-1, 2)
    obj_pt *= SQUARE_SIZE

    obj_points, img_points = [], []
    img_size = None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] 동영상을 열 수 없어요: {video_path}")
        sys.exit(1)

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"[INFO] 동영상: {total}프레임 | 매 {FRAME_SKIP}프레임마다 탐색 중...")

    frame_idx, detected = 0, 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        if frame_idx % FRAME_SKIP != 0:
            continue

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(gray, board_size, None)
        if found:
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            obj_points.append(obj_pt)
            img_points.append(corners2)
            img_size = gray.shape[::-1]
            detected += 1
            print(f"  ✓ {detected}장 수집 (프레임 {frame_idx}/{total})")

            if preview:
                vis = frame.copy()
                cv2.drawChessboardCorners(vis, board_size, corners2, found)
                cv2.putText(vis, f"Collected: {detected}", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.imshow("Calibration Preview", vis)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    cap.release()
    cv2.destroyAllWindows()

    if detected < MIN_SAMPLES:
        print(f"[ERROR] 샘플 부족: {detected}장 (최소 {MIN_SAMPLES}장 필요)")
        print("  → FRAME_SKIP을 줄이거나 더 긴 동영상을 사용하세요.")
        sys.exit(1)

    print(f"\n[INFO] {detected}장으로 캘리브레이션 중...")
    _, K, dist, rvecs, tvecs = cv2.calibrateCamera(
        obj_points, img_points, img_size, None, None)

    total_err = 0
    for i in range(len(obj_points)):
        proj, _ = cv2.projectPoints(obj_points[i], rvecs[i], tvecs[i], K, dist)
        total_err += cv2.norm(img_points[i], proj, cv2.NORM_L2) / len(proj)
    print(f"[RESULT] 재투영 오차: {total_err/len(obj_points):.4f} px  (낮을수록 좋음)")
    print(f"[RESULT] Camera Matrix:\n{K}")

    np.savez(CALIB_FILE, camera_matrix=K, dist_coeffs=dist)
    print(f"[SAVED] → {CALIB_FILE}")

    # 왜곡 보정 영상 저장
    print("\n[INFO] 왜곡 보정 영상 저장 중...")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter("undistorted_output.avi",
                          cv2.VideoWriter_fourcc(*"XVID"), fps, (w, h))
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        undistorted = cv2.undistort(frame, K, dist)
        out.write(undistorted)
    cap.release()
    out.release()
    print("[SAVED] → undistorted_output.avi")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AR Chessboard Viewer")
    
    parser.add_argument("--video",   required=True,        help="입력 동영상 경로 (.mp4 등)")
    parser.add_argument("--preview", action="store_true",  help="캘리브레이션 미리보기")
    args = parser.parse_args()

    run_calibration(args.video, preview=args.preview)