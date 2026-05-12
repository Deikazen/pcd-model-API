import cv2


def extracted_feature(binary_image):

    contours, _ = cv2.findContours(
        binary_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    total_area = 0
    total_perimeter = 0
    crack_count = 0

    valid_contours = []

    for cnt in contours:

        area = cv2.contourArea(cnt)

        # filter noise kecil
        if area > 100:

            x, y, w, h = cv2.boundingRect(cnt)  # Q
            aspect_ratio = float(w) / h if h != 0 else 0

            if aspect_ratio > 1.5 or aspect_ratio < 0.7:

                perimeter = cv2.arcLength(cnt, True)

                total_area += area
                total_perimeter += perimeter
                crack_count += 1

                valid_contours.append(cnt)

    features = {
        "total_area": total_area,
        "total_perimeter": total_perimeter,
        "crack_count": crack_count
    }

    return features, valid_contours
