import cv2
import base64
import numpy as np
import fingerprint_enhancer

# Sample Base64-encoded fingerprint strings (Replace with actual fingerprints)
fingerprint_base64_1 = "MjAyNS0wMy0yMFQyMToxODo0MZfYKRjT5HKj3LMrkIqoMhWSfXVKV+b/0lI9G9Cc2nuucdMHEAGTjoJA6BOONVzQZJplgE2PZ+GJY680WmSYaSe1YRGfeuhYr7U4ry3FQvcvNFQrwrnpdNYC6HrESQ1DnG6zPGwRbQTrhU5B511W3hUlCStziyHHy7R57wUC+kf2H/zVoPu1H9iuSFA3+XMDW0FewwOJ08v3BAI1ne86gj8tTRvP6st64oUwkKDpjGq2gFlKr7jRT3DKzyNPPpndjDEV3vZbU0npzSn6rOjvmhi/rTAQbNs2olbqWKvbR7gU6hUeaqcAz+fcsPor42t82UROTLEGy1IBz76zDuiOvyR+5DV9ePgcXklN8t+/O60oQ4/8cFQnPMN/UrRmPFfFDJqcBgNIVJXAHnuwBbkA3XUZihWIXlLq1/AW5lpAvDlEeHf79yWLiVi9IBrrTFxRMs1nPQdhcQ6L+SFBMExtn2W1YdoKKWwMIKvo+2fgIVDLPXn5GxfEN+ddT924xc36YrL9QKn+CiJr/gxVO3i9NBekielHcwYPLbmAnujLsw95fkybYSoSILz3WLJr/JbkE322RaWT2hMfDfugF5Wyk+EoRsLr5MrQthHEIDVll0uz1bG88PMjCaTeNmcHZGf15RzivPayYG+PilhzvhYIiwCDyuhdVY237S4j+m6UbernKAMhGHWPozicORXz2s/aPnXrv5C2Glykke3NLhtxOeM7PFxol0VS6K0Mdv+ARfX7tI3dT3kQ1hEQto5pMudeUGzcVrkNRH5ubLkFXrrqVsN7u9EoWwyRcDbNxGZq4yUIYmcZmO4Xzqc+X96Ky3pk02SSaJyUdjc3x9uvmgDPHLhCv3MTopIdiHKa5klua8hFuCIs669LcjyNtOp1m3B/cKNwucfQjnyU4hFOrzvTPZg2ohB6MvrV68UA8HSlzHROJ7/mHDxs/ynSohbM62mP/c0DDyLWAXiKSsceYCre7/lacFaQTnMMFLnnYF3oI0IGq6pviLPfnFt4mCvFBbE7pFajgIg6qV46GC2p9IlLSTdHL8ls7vAyP6NGH63QrCobf3lIEhYvnVBO5Q6o02SGNdy6fBYw473gGzIJ1aReEWb862OenfiBhFlZLPOu7e5uki1e4RHFK/ibYswTQpKtqtKpFiW2TGnW8rJQHCS/rg7loWcF27GbScbVRjtL6E/T3GiBpAqxdHQ0/VvUhkODMsOmBizfeRtNSJYiejLVDKvW+m4pLJ27xQVA3WWHhVWDIX+bw6JUEgwUZe5eLcFCQigwVPsnv/+h/pf4FYERlDJzNFMT97NPm/qkeliKSwg6cmnsEi2cLsE3oU+kpklc+qy6B2Aijicx8MfEuXDYkn4kX4YLp/8mxq33eZ5130afZmMFip6FeYR4LBt15g7cZ4F4fIl1H6Gade7MTUN3psM6U93DxlJFkVlhU3W+zeEEfJGeeffs+I/d5jcbzqJMybKS8nUpz1v24tuq0qpUzscL+8PvLg4UnjbeihQOy2vm6c/vaKmjp888Xj/1OCPvwesLPJLT3e2Ep6kNIli3rsPidShWITi/qx95Qg3W2FUCcRui9BbfC53RSutUbm9fWk3R4tNTpVs2WoqU53Gkj4JwX+hOQoSHFDjf5fzYdLtVyklL1KyDOtMIpfn8NjFphUvlOlw="
fingerprint_base64_2 = "MjAyNS0wMy0yMFQyMToxODo0MZfYKRjT5HKj3LMrkIqoMhWSfXVKV+b/0lI9G9Cc2nuucdMHEAGTjoJA6BOONVzQZJplgE2PZ+GJY680WmSYaSe1YRGfeuhYr7U4ry3FQvcvNFQrwrnpdNYC6HrESQ1DnG6zPGwRbQTrhU5B511W3hUlCStziyHHy7R57wUC+kf2H/zVoPu1H9iuSFA3+XMDW0FewwOJ08v3BAI1ne86gj8tTRvP6st64oUwkKDpjGq2gFlKr7jRT3DKzyNPPpndjDEV3vZbU0npzSn6rOjvmhi/rTAQbNs2olbqWKvbR7gU6hUeaqcAz+fcsPor42t82UROTLEGy1IBz76zDuiOvyR+5DV9ePgcXklN8t+/O60oQ4/8cFQnPMN/UrRmPFfFDJqcBgNIVJXAHnuwBbkA3XUZihWIXlLq1/AW5lpAvDlEeHf79yWLiVi9IBrrTFxRMs1nPQdhcQ6L+SFBMExtn2W1YdoKKWwMIKvo+2fgIVDLPXn5GxfEN+ddT924xc36YrL9QKn+CiJr/gxVO3i9NBekielHcwYPLbmAnujLsw95fkybYSoSILz3WLJr/JbkE322RaWT2hMfDfugF5Wyk+EoRsLr5MrQthHEIDVll0uz1bG88PMjCaTeNmcHZGf15RzivPayYG+PilhzvhYIiwCDyuhdVY237S4j+m6UbernKAMhGHWPozicORXz2s/aPnXrv5C2Glykke3NLhtxOeM7PFxol0VS6K0Mdv+ARfX7tI3dT3kQ1hEQto5pMudeUGzcVrkNRH5ubLkFXrrqVsN7u9EoWwyRcDbNxGZq4yUIYmcZmO4Xzqc+X96Ky3pk02SSaJyUdjc3x9uvmgDPHLhCv3MTopIdiHKa5klua8hFuCIs669LcjyNtOp1m3B/cKNwucfQjnyU4hFOrzvTPZg2ohB6MvrV68UA8HSlzHROJ7/mHDxs/ynSohbM62mP/c0DDyLWAXiKSsceYCre7/lacFaQTnMMFLnnYF3oI0IGq6pviLPfnFt4mCvFBbE7pFajgIg6qV46GC2p9IlLSTdHL8ls7vAyP6NGH63QrCobf3lIEhYvnVBO5Q6o02SGNdy6fBYw473gGzIJ1aReEWb862OenfiBhFlZLPOu7e5uki1e4RHFK/ibYswTQpKtqtKpFiW2TGnW8rJQHCS/rg7loWcF27GbScbVRjtL6E/T3GiBpAqxdHQ0/VvUhkODMsOmBizfeRtNSJYiejLVDKvW+m4pLJ27xQVA3WWHhVWDIX+bw6JUEgwUZe5eLcFCQigwVPsnv/+h/pf4FYERlDJzNFMT97NPm/qkeliKSwg6cmnsEi2cLsE3oU+kpklc+qy6B2Aijicx8MfEuXDYkn4kX4YLp/8mxq33eZ5130afZmMFip6FeYR4LBt15g7cZ4F4fIl1H6Gade7MTUN3psM6U93DxlJFkVlhU3W+zeEEfJGeeffs+I/d5jcbzqJMybKS8nUpz1v24tuq0qpUzscL+8PvLg4UnjbeihQOy2vm6c/vaKmjp888Xj/1OCPvwesLPJLT3e2Ep6kNIli3rsPidShWITi/qx95Qg3W2FUCcRui9BbfC53RSutUbm9fWk3R4tNTpVs2WoqU53Gkj4JwX+hOQoSHFDjf5fzYdLtVyklL1KyDOtMIpfn8NjFphUvlOlw="
try:
    base64.b64decode(fingerprint_base64_1)
    print("✅ Base64 string is valid!")
except Exception as e:
    print("❌ Invalid Base64 string:", e)
# Function to convert Base64 string to image
def save_fingerprint_image(base64_string, output_path):
    fingerprint_bytes = base64.b64decode(base64_string)  # Decode Base64
    np_array = np.frombuffer(fingerprint_bytes, dtype=np.uint8)  # Convert to NumPy array
    image = cv2.imdecode(np_array, cv2.IMREAD_GRAYSCALE)  # Decode into grayscale image

    if image is None:
        raise ValueError("Error: Unable to decode fingerprint data into an image.")

    cv2.imwrite(output_path, image)  # Save the image
    return output_path

# Function to enhance fingerprint image
def enhance_fingerprint(image_path, output_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        raise ValueError(f"Error: Could not load image from {image_path}.")

    enhanced_img = fingerprint_enhancer.enhance_fingerprint(img)  # Enhance fingerprint
    cv2.imwrite(output_path, enhanced_img)  # Save enhanced image
    return output_path

# Function to compare fingerprints using ORB feature matching
def compare_fingerprints(image1_path, image2_path):
    img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        raise ValueError("Error: Could not load one or both fingerprint images.")

    orb = cv2.ORB_create()  # ORB Detector
    kp1, des1 = orb.detectAndCompute(img1, None)  # Keypoints & Descriptors for Image 1
    kp2, des2 = orb.detectAndCompute(img2, None)  # Keypoints & Descriptors for Image 2

    if des1 is None or des2 is None:
        raise ValueError("Error: No features found in one or both images.")

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)  # Brute-force matcher
    matches = bf.match(des1, des2)  # Match descriptors

    matches = sorted(matches, key=lambda x: x.distance)  # Sort matches by distance

    similarity_score = len(matches) / max(len(des1), len(des2))  # Normalized similarity score

    return similarity_score

# Convert and save images
image1_path = "fingerprint1.png"
image2_path = "fingerprint2.png"

enhanced_image1_path = "enhanced_fingerprint1.png"
enhanced_image2_path = "enhanced_fingerprint2.png"

try:
    save_fingerprint_image(fingerprint_base64_1, image1_path)
    save_fingerprint_image(fingerprint_base64_2, image2_path)

    enhance_fingerprint(image1_path, enhanced_image1_path)
    enhance_fingerprint(image2_path, enhanced_image2_path)

    similarity = compare_fingerprints(enhanced_image1_path, enhanced_image2_path)
    print(f"🔹 Fingerprint Similarity Score: {similarity:.2f}")

    if similarity > 0.4:  # Threshold (Adjust as needed)
        print("✅ Fingerprints Match!")
    else:
        print("❌ Fingerprints Do Not Match.")

except Exception as e:
    print(f"Error: {e}")
