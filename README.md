# 📌 Camera Calibration & Distortion Correction

OpenCV를 사용하여 체스보드 패턴 기반 카메라 캘리브레이션을 수행하고, 추정된 파라미터를 이용해 렌즈 왜곡 보정을 구현했다.

---

## ⚙️ 실행 방법

```bash
python camera-calibration.py --calibrate --video input.mp4
````

---

## 📊 Calibration 결과

* **Reprojection Error (RMSE)**
  → 0.0498 px

* **Camera Matrix (Intrinsic Parameters)**

```
fx = 868.3925
fy = 868.6429
cx = 548.7791
cy = 952.1690
```

---

## 📐 설정 정보

* Chessboard Size: **7 x 7 (inner corners)**
* Square Size: **0.025 m**
* Calibration Frames Used: **53 frames**

---

## 🎥 결과

### Distortion Correction

<p align="center">
  <img src="https://github.com/user-attachments/assets/d6d220af-b5a6-474a-a229-2bf662162210" width="45%">
  <img src="https://github.com/user-attachments/assets/44e3c569-0686-4a61-81c8-8514650be5c5" width="45%">
</p>

