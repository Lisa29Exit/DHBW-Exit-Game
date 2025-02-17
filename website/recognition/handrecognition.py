import mediapipe as mp
import cv2, time
import numpy as np
from math import atan2, degrees

class Timer:
    def __init__(self):
        self.start_time = None
        self.duration = 0
        self.running = False

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True

    def stop(self):
        if self.running:
            self.duration = time.time() - self.start_time
            self.running = False

    def reset(self):
        self.start_time = None
        self.duration = 0
        self.running = False

    def get_duration(self):
        if self.running:
            return time.time() - self.start_time
        return self.duration

    def is_running(self):
        return self.running



def recognise():
  mp_drawing = mp.solutions.drawing_utils
  mp_hands = mp.solutions.hands

  #open video from camera
  cap = cv2.VideoCapture(0)

  #create an instance of the gesture Timer class
  timer = Timer()
  THUMBS_UP_HOLD_TIME = 3
  #create hand recognition model
  with mp_hands.Hands(max_num_hands = 1, min_detection_confidence = 0.7, min_tracking_confidence = 0.5) as hands:

    print('press "q" to exit')
    while cap.isOpened():
      #read every frame 
      ret, frame = cap.read()
      if not ret:
        break
      
      #mediapipe recognition
      #feed from openCV is in BGR and needs to be set to RGB
      image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      image.flags.writeable = False


      #detect
      results = hands.process(image)

      image.flags.writeable = True
      #back to BGR for displaying
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      

      #draw landmarks on camera feed one frame at the time
      if results.multi_hand_landmarks:
        thumb_up = False
        thumb_angle = False
        curled_distance = []

        for num, hand in enumerate(results.multi_hand_landmarks):
          #draw landmarks and connections
          mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS,
                                    #make lines look pretty
                                    mp_drawing.DrawingSpec(color=(121, 22, 76), thickness = 2, circle_radius = 4),
                                    mp_drawing.DrawingSpec(color=(121, 44, 250), thickness = 2, circle_radius = 2))


          #process if there is a "thumbs up"
          #thumbs up is if thumb is raised and others are curled
          thumb_tip = hand.landmark[mp_hands.HandLandmark.THUMB_TIP] 
          thumb_mcp = hand.landmark[mp_hands.HandLandmark.THUMB_MCP] 
          middle_finger_mcp = hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
          wrist = hand.landmark[mp_hands.HandLandmark.WRIST]
          other_tips = [mp_hands.HandLandmark.INDEX_FINGER_TIP,
                        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                        mp_hands.HandLandmark.RING_FINGER_TIP,
                        mp_hands.HandLandmark.PINKY_TIP]
          other_mcp = [mp_hands.HandLandmark.INDEX_FINGER_MCP,
                        mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
                        mp_hands.HandLandmark.RING_FINGER_MCP,
                        mp_hands.HandLandmark.PINKY_MCP]

          #check if thumb is pointing up (rotation)
          angle_radians = atan2(thumb_mcp.y - thumb_tip.y,
                                thumb_mcp.x - thumb_tip.x)
          angle_degrees = degrees(angle_radians)

          # Adjust angle to the range 0 to 360 degrees
          if angle_degrees < 0:
              angle_degrees += 360

          if 60 <= angle_degrees <= 120:
            thumb_angle = True

          # thumb is over other tips
          if hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < thumb_tip.y:
            thumb_up = False
          else:
            thumb_up = True

          for i in range(len(other_tips)):
            #check distance between other tips and wrist (check if curled)
            finger_tip_landmark = hand.landmark[other_tips[i]] 
            finger_mcp_landmark = hand.landmark[other_mcp[i]] 

            middle_point = ([(wrist.x + finger_mcp_landmark.x) / 2, 
                            (wrist.y + finger_mcp_landmark.y) / 2,
                            (wrist.z + finger_mcp_landmark.z) / 2])

            finger_point = np.array([finger_tip_landmark.x, finger_tip_landmark.y, finger_tip_landmark.z])
            distance = np.linalg.norm(middle_point - finger_point)

            #accepted distance gets expandet if fingers are behind hand
            if (finger_tip_landmark.z > finger_mcp_landmark.z):
              pass

            if distance > 0.1:
              curled_distance.append(False)
            else:
              curled_distance.append(True)


          #calculate if is thubs up
          curled_true = sum(curled_distance)  
          curled_false = len(curled_distance) - curled_true
          
          total_elements = len(curled_distance)
          if total_elements == 0:
            break
          percent_true = (curled_true / total_elements) * 100

          # print("Curled percentage:  ", percent_true,
          #       "  curled distance", curled_distance,

          #       "  Thumb up:", thumb_up,
          #       "  thumb_angle: ", thumb_angle)
          
        
          #if thumb up, then show text
          if percent_true > 80 and thumb_up and thumb_angle:
            thumbs_up_duration = 0
            if not timer.is_running():
              timer.start()
            else:
              thumbs_up_duration = timer.get_duration()

            if thumbs_up_duration >= THUMBS_UP_HOLD_TIME:
              timer.stop()
              text = "completed"
              font_scale = 4
              font_thickness = 7
              text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
              text_x = (image.shape[1] - text_size[0]) // 2
              text_y = (image.shape[0] + text_size[1]) // 2    
              cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (127, 51, 171), font_thickness)
              cv2.imshow('Hand Tracking', image)
              cv2.waitKey(2000)  # Wait for 2 seconds to display the success message
              cap.release()
              cv2.destroyAllWindows()
              return True
            else:
              progress = int((thumbs_up_duration / THUMBS_UP_HOLD_TIME) * 300)
              cv2.rectangle(image, (10, 40), (10 + progress, 60), (127, 51, 171), -1)
              cv2.putText(image, f'Time: {thumbs_up_duration:.1f}s', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (127, 51, 171), 2)
          else:
            timer.reset()
          
            # cv2.putText(image, f'Daumen hoch!', (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
            #             1, (144, 255, 0), 2)

      


      #render image from mediapipe
      cv2.imshow('Hand Tracking', image)

      #cancel if q is pressed
      if cv2.waitKey(10) & 0xFF == ord('q'):
        break

    cap.release()
    cv2.destroyAllWindows()
