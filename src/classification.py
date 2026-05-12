
def classification(total_area):

    if total_area < 100:
        return "NON CRACK"

    elif total_area > 200 and total_area < 500:
        return "LIGHT CRACK"

    elif total_area > 500 and total_area < 1000:
        return "MEDIUM CRACK"

    elif total_area > 1000:
        return "HEAVY CRACK"
