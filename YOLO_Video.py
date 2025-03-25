from ultralytics import YOLO
import cv2
import math
import pandas as pd
import os

def display_alert(img, message):
    # Display the alert message on the top of the image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, message, (50, 50), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

def process_image(image_path):
    model = YOLO("best.pt")
    classNames = ['fight', 'panic', 'suspicious package']

    # Dictionary to store counts of each detected class
    object_counts = {class_name: 0 for class_name in classNames}

    img = cv2.imread(image_path)
    results = model(img)
    alert_message = ""

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            class_name = classNames[cls]

            # Debugging output
            print(f"Detected {class_name} with confidence {conf}")

            # Update the count of the detected object
            if class_name in object_counts:
                object_counts[class_name] += 1
                alert_message = f"Alert: {class_name} detected!"

            # Draw bounding box and label
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            label = f'{class_name} {conf}'
            t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
            c2 = x1 + t_size[0], y1 - t_size[1] - 3
            cv2.rectangle(img, (x1, y1), c2, [255, 0, 255], -1, cv2.LINE_AA)  # filled
            cv2.putText(img, label, (x1, y1 - 2), 0, 1, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

    # Display alert message if any abnormal activity is detected
    if alert_message:
        display_alert(img, alert_message)

    # Save the processed image
    output_image_path = os.path.splitext(image_path)[0] + "_output.jpg"
    cv2.imwrite(output_image_path, img)

    # Display the processed image
    cv2.imshow("Processed Image", img)
    cv2.waitKey(0)  # Wait until a key is pressed
    cv2.destroyAllWindows()

    # Save the counts to an Excel file
    try:
        df = pd.DataFrame(list(object_counts.items()), columns=['Object', 'Count'])
        output_file = "object_counts.xlsx"
        if os.path.exists(output_file):
            os.remove(output_file)  # Remove the file if it exists
        df.to_excel(output_file, index=False)
        print("Updated object counts saved to object_counts.xlsx")
    except PermissionError:
        print("Permission denied: unable to save the file. Please close any open instances of the file and try again.")

    print("Object counts:", object_counts)

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    model = YOLO("best.pt")
    classNames = ['fight', 'panic', 'suspicious package']

    # Dictionary to store counts of each detected class
    object_counts = {class_name: 0 for class_name in classNames}

    frame_count = 0
    alert_message = ""

    while True:
        success, img = cap.read()
        if not success:
            break

        frame_count += 1
        if frame_count % 10 == 0:  # Process every 10th frame for efficiency
            results = model(img, stream=True)
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    conf = math.ceil((box.conf[0] * 100)) / 100
                    cls = int(box.cls[0])
                    class_name = classNames[cls]

                    # Debugging output
                    print(f"Detected {class_name} with confidence {conf}")

                    # Update the count of the detected object
                    if class_name in object_counts:
                        object_counts[class_name] += 1
                        alert_message = f"Alert: {class_name} detected!"

                    # Draw bounding box and label
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    label = f'{class_name} {conf}'
                    t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                    c2 = x1 + t_size[0], y1 - t_size[1] - 3
                    cv2.rectangle(img, (x1, y1), c2, [255, 0, 255], -1, cv2.LINE_AA)  # filled
                    cv2.putText(img, label, (x1, y1 - 2), 0, 1, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

            # Display alert message if any abnormal activity is detected
            if alert_message:
                display_alert(img, alert_message)

            # Show the processed video frame
            cv2.imshow("Processed Video", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
                break

    cap.release()
    cv2.destroyAllWindows()

    # Save the counts to an Excel file
    try:
        df = pd.DataFrame(list(object_counts.items()), columns=['Object', 'Count'])
        output_file = "object_counts.xlsx"
        if os.path.exists(output_file):
            os.remove(output_file)  # Remove the file if it exists
        df.to_excel(output_file, index=False)
        print("Updated object counts saved to object_counts.xlsx")
    except PermissionError:
        print("Permission denied: unable to save the file. Please close any open instances of the file and try again.")

    print("Object counts:", object_counts)

def video_detection(path):
    if path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        process_video(path)
    elif path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        process_image(path)
    else:
        print("Unsupported file format")

# Example usage
video_detection('path_to_your_video_or_image_file')
