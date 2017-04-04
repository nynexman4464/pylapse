import cv2
import time
import sys,os
from optparse import OptionParser

#This is for detecting key press
import platform
if platform.system() == 'Windows':
    import msvcrt
else:
    import select

def init_cam(device_id,width,height):
    cam = cv2.VideoCapture(device_id)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cam

#######
# fps - the fps of the output movie (hz)
# timelapse_sleep - the amount of time between frames
#cam_idx - the camera idx (if only one camera it should be  0)
#height - the image height in pixels
#width - the image width in pixels
#######
def start_timelapse(fps,timelapse_sleep,cam_idx,height,width,output_dir,quality) :

    #initiate the camera 
    cam = init_cam(cam_idx,width,height)

    #the frame idx, how much frames has been captured
    idx = 1
    
    #A timer for debug prints
    tic = time.time()
    
    #the image name scheme
    image_name_format = "%s/%d-%%d.jpg" % (output_dir, time.time())
    print image_name_format
    try:
        while True:
            
            #capture a photo from the camera
            ret, img_rgb = cam.read()
            if ret:
                #embed the frame idx in the naming scheme
                img_name = image_name_format % idx
                
                #save the photo
                cv2.imwrite(img_name,img_rgb,[int(cv2.IMWRITE_JPEG_QUALITY), quality])
                
        
                #debug print to see some progress
                if time.time() - tic > 5:
                    print 'created %d images' %(idx)
                    tic = time.time()
        
                    #sleep between 2 frames
                time.sleep(timelapse_sleep)
                    
                idx = idx + 1
    except KeyboardInterrupt:
        print "saving"
            
    #After finishing the capture loop we can start creating the timelapse
    os.system('ffmpeg -framerate %d -i %s -c:v libx264 -r 20 -pix_fmt yuv420p %s/%d.mp4' % (fps,image_name_format,output_dir,int(time.time())))

def preview_cam(cam_idx,height,width):
    cam = init_cam(cam_idx,width,height)
    print cam_idx,width,height
    while(True):
        # Capture frame-by-frame
        ret, frame = cam.read()
        
        #if we really got a frame
        if ret:

            # Our operations on the frame come here
            #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
            # Display the resulting frame
            cv2.imshow('frame',frame)
            
            #Check if we capture the q key we exit the program
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    # When everything done, release the capture
    cam.release()
    cv2.destroyAllWindows()

def main():

    parser = OptionParser()

    parser.add_option("-p", "--preview", dest="preview",
                      default=False,
                      help="Preview the camera")
    parser.add_option("-t", "--timelapse",
                      default=False,
                      help="start taking pictures for the timelapse")
    parser.add_option("-w", "--width",
                      default=640,
                      help="camera image width in pixels")
    parser.add_option("-l", "--height",
                      default=480,
                      help="camera image height in pixels")
    parser.add_option("-c", "--cam_idx",
                      default=0,
                      help="camera index")
    parser.add_option("-f", "--fps",
                      default=30,
                      help="video output fps")
    parser.add_option("-i", "--interval",
                      default=10,
                      help="interval between frames")
    parser.add_option("-o", "--output-dir",
                      default='.',
                      help="the folder it would create the images and the video")
    parser.add_option("-q", "--quality",
                      default=90,
                      help="image quality of the compression")

    (options, args) = parser.parse_args()
    
    output_dir = options.output_dir    
    if os.path.isdir(output_dir) == False:
        print "%s doesn't exist please choose another folder" % output_dir
        exit(0)

    cam_idx = options.cam_idx#int(options.cam_idx)
    height = int(options.height)
    width = int(options.width)
    
    if bool(options.preview):
        preview_cam(cam_idx,height,width)
        
    elif bool(options.timelapse):
        fps = int(options.fps)
        interval = float(options.interval)
        quality = int(options.quality)
        start_timelapse(fps,interval,cam_idx,height,width,output_dir,quality)
        
if __name__ == "__main__":
    main()
