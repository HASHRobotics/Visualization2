#!/usr/bin/env python
import rospy
import numpy as np
from numpy import genfromtxt
import random
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import style
import pdb
from math import cos,sin,radians
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import cv2
import skvideo
# skvideo.setFFmpegPath('/usr/local/lib/python2.7/dist-packages/ffmpeg/')
import skvideo.io

#=========================================================================================================================================

fig,((ax1,ax2),(ax3,ax4)) = plt.subplots(2,2)
# fig, (ax1,ax2) = plt.subplots(1,2)
count = 0
global_least_euclidian_distances = []
global_pit_edges = []
local_least_euclidian_distances = []
g_number_of_waypoints_within_threshold = 0
global_waypoints_threshold_distance = 15	# distance in (m)
index =0
inF=skvideo.io.vread('src/visualization/data/test_vid.mp4')

#==========================================================================================================================================
#ax1.set_title(r'Range VS Time')
#ani = 1
# global_waypoint_distance_values = []
# global_waypoint_count = 0 	#to see how any entries range values has and then plot only when new values come
# global_waypoints_mean_distance = 0

# def global_waypoint_dist_callback(distance):
# 	global global_waypoint_distance_values
# 	global_waypoint_distance_values.append(distance.range + random.randint(1,30))

def pit_image_callback(msg):			#Use the msg.flag to see if you need to keep publishing old message or use the new one
	rospy.loginfo('Image received...')
	image = CvBridge().imgmsg_to_cv2(msg)
	ax2.imshow(image)
	ax2.axis('off')

def get_least_euclidian_distances(global_waypoints,pit_edges):
	least_euclidian_distances = []
	number_of_waypoints_within_threshold = 0
	for i in range(global_waypoints.shape[0]):
		dist = np.asscalar(np.min(np.linalg.norm(global_waypoints[i,:] - pit_edges, axis=1)))
		least_euclidian_distances.append(dist)

		if(dist<global_waypoints_threshold_distance):
			number_of_waypoints_within_threshold+=1

	return least_euclidian_distances,number_of_waypoints_within_threshold

def get_global_waypoints_data():
	pit_edges_file_name = "src/visualization/data/pit_edges.csv"
	global_waypoints_file_name = "src/visualization/data/global_waypoints.csv"
	global_waypoints = genfromtxt(global_waypoints_file_name, delimiter=',')		#TODO: Resolution transform these global waypoints
	pit_edges = genfromtxt(pit_edges_file_name, delimiter=',')
	least_euclidian_distances,number_of_waypoints_within_threshold = get_least_euclidian_distances(global_waypoints,pit_edges)
	return least_euclidian_distances,pit_edges,number_of_waypoints_within_threshold

def local_waypoints_callback(msg):			#Use the msg.flag to see if this is the last point before the state machien transitions for a new state
	rospy.loginfo('New local waypoint received...')
	if(msg.flag):
		local_least_euclidian_distances.append(np.asscalar(np.min(np.linalg.norm(np.array([msg.x,msg.y]) - global_pit_edges, axis=1))))

# def plot_video():
# 	global ax3
# 	filename = 'src/visualization/data/test_vid.mp4'
# 	cap = cv2.VideoCapture(filename)

# 	frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# 	# width  = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
# 	# height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

# 	# fig, ax = plt.subplots(1,1)
# 	# plt.ion()
# 	# plt.show()

# 	#Setup a dummy path

# 	for i in range(frames):
# 		fig.clf()
# 		flag, frame = cap.read()

# 		ax3.imshow(frame)
# 		if cv2.waitKey(1) == 27:
# 			break 

def set_font_size(ax):
	for label in (ax.get_xticklabels() + ax.get_yticklabels()):
		label.set_fontname('Arial')
		label.set_fontsize(28)

def animate(frames):
	global ax1
	# global ax2
	# global ax3
	# global global_waypoint_distance_values
	# global global_waypoint_count
	global g_number_of_waypoints_within_threshold
	global index
	global inF
	global count
	global global_least_euclidian_distances
	global global_pit_edges
	rospy.loginfo("In Animate \n")

	if(count==0):
		least_euclidian_distances,pit_edges,number_of_waypoints_within_threshold = get_global_waypoints_data()	
		global_least_euclidian_distances = least_euclidian_distances
		g_number_of_waypoints_within_threshold = number_of_waypoints_within_threshold
		global_pit_edges = pit_edges
		print("Distances calculated")
		count+=1
	else:
		least_euclidian_distances = global_least_euclidian_distances
		number_of_waypoints_within_threshold = g_number_of_waypoints_within_threshold

	ax1.clear()
	average = sum(least_euclidian_distances) / len(least_euclidian_distances)
	x = np.arange(len(least_euclidian_distances))  # the label locations
	width = 0.35  # the width of the bars

	rects1 = ax1.bar(x - width/2, least_euclidian_distances, width, label='')

	# _, ymax = ax1.get_ylim()
	ax1.set_ylabel('Distance of global waypoints from pit edge (m)',fontsize=28)
	ax1.set_xlabel('Global Waypoint number',fontsize=28)
	set_font_size(ax1)
	ax1.set_title('Distances of global waypoints from pit edge',fontsize=28)
	ax1.hlines(y=average, xmin=-1, xmax=len(x), linestyle='--', color='r')
	ax1.text(-1*0.9, average*1.02, 'Mean: {:.2f}'.format(average),fontsize=28)

	# place a text box in upper left in axes coords
	textstr = '% of waypoints within threshold: {:.2f}'.format(number_of_waypoints_within_threshold*100/len(least_euclidian_distances))
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props, weight='bold')
	ax1.set_xticks(x)
	ax1.set_xticklabels(x)
	ax1.legend()
	autolabel(rects1,ax1)
	# fig.tight_layout()

	''' Future code to be used once Ayush's topic exists'''
	# ax2.clear()
	# local_average = sum(local_least_euclidian_distances) / len(local_least_euclidian_distances)
	# local_x = np.arange(len(least_euclidian_distances))
	# rects2 = ax2.bar(local_x - width/2, local_least_euclidian_distances, width, label='')

	# ax2.set_ylabel('Distance of local waypoints from pit edge (m)')
	# ax2.set_title('Distances of local waypoints from pit edge')
	# set_font_size(ax2)
	# ax2.hlines(y=local_average, xmin=-1, xmax=len(local_x), linestyle='--', color='r')
	# ax2.text(-1*0.9, average*1.02, 'Mean: {:.2f}'.format(local_average))
	# ax2.set_xticks(local_x)
	# ax2.set_xticklabels(local_x)
	# ax2.legend()
	# autolabel(rects2,ax2)	

	'''Plot Video'''
	# pdb.set_trace()

	# while i in range(inF.shape[0]):
	# 	im1 = ax1.imshow(grab_frame(i))
	# 	im1.set_data(grab_frame(i))

def grab_frame(i):
	global inF
	frame = inF[i]
	return cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

def autolabel(rects,ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{0:.2f}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom',size=15)


if __name__ == '__main__':
	rospy.init_node('visualize', anonymous=True)
	# rospy.Subscriber("/global_waypoint_dist", Range, global_waypoint_dist_callback)
	rospy.Subscriber("/apnapioneer3at/MultiSense_S21_meta_camera/image",Image,pit_image_callback)
	rate = rospy.Rate(50)
	rospy.loginfo("In Main \n")
	ani = animation.FuncAnimation(fig,animate,frames = None,interval = 50)
	# movie = Movie_MP4(r"src/visualization/data/test_vid.mp4")
	# if raw_input("Press enter to play, anything else to exit") == '':
	# 	movie.play()
	while not rospy.is_shutdown():
		plt.show()
		rate.sleep()