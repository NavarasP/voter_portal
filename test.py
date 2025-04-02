import cv2

# Open the camera (0 for default, 1 for external)
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("❌ Error: Could not access the camera. Please check permissions or if another app is using it.")
else:
    print("✅ Camera accessed successfully!")

    # Capture a frame to test
    ret, frame = cap.read()
    if ret:
        cv2.imshow("Camera Test", frame)
        cv2.waitKey(3000)  # Display for 3 seconds
        cv2.destroyAllWindows()
    else:
        print("❌ Error: Could not read frame from camera.")

# Release the camera
cap.release()
