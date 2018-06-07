# This standalone Python script performs kmeans on the given data.
# Since kmeans is susceptible to local optima, the algorithm is run num_runs times.
# The run with the lowest distortion is chosen as the final clustering.
#______________________________________________

from sklearn.cluster import KMeans
import numpy as np
import csv

# Set this to the name of the csv containing the training data.
training_data = "feature_vectors.csv"

# Set this to the name of the csv containing the NORMALIZED training data.
normalized_training_data = "normalized_feature_vectors.csv"

# Change this to the desired number of clusters to be fit to the data.
num_clusters = 4

# Number of times the kmeans algorithm will be performed.
num_runs = 10

# Global list of tuples: (address, rank)
addr_list = []

# If just loading a numpy don't need to mess with CSV reading
loading_npy_array = True

# To use standard feature vectors without normalization, set usingNormalizedFeats to False.
# Set verbose to False to not print results after fitting.
# After each run, checks if a lower distortion was given.
# If so, cluster assignments are updated accordingly.
#______________________________________________

def main():
	#print("Don't want to overwrite existing data...")
	#return

	global num_runs
	saveLargestCluster = False
	verbose = False
	usingNormalizedFeats = True
	if (not loading_npy_array):
		data = format_data(usingNormalizedFeats)
	else:
		if usingNormalizedFeats:
			data = np.load("Final_Normalized_Feature_Vectors_Minus_Oultiers.npy")
		else:
			data = np.load("Final_Feature_Vectors_Minus_Outliers.npy")
	cluster_centroids = []
	cluster_assignments = []
	distortion = 0.0
	for run in range(num_runs):
		result = run_kmeans(data, verbose)
		if (run is 0):
			cluster_centroids = result[0]
			cluster_assignments = result[1]
			distortion = compute_distortion(data, cluster_centroids, cluster_assignments)
		else:
			curr_distortion = compute_distortion(data, result[0], result[1])
			if (curr_distortion < distortion):
				distortion = curr_distortion
				cluster_centroids = result[0]
				cluster_assignments = result[1]

	if(saveLargestCluster):
		# Save all points in larger cluster as numpy array
		# We will run PCA on these points
		final_result = []
		for index in range(len(cluster_assignments)):
			if (cluster_assignments[index] == 0):
				final_result.append(data[index])
		final_result = np.array(final_result)
		np.save("Largest_Cluster.npy", final_result)

	result = []
	print ("")
	print ("")
	print ("Here are the final cluster centroids and assignments:")
	print ("")
	result.append(cluster_centroids)
	for cluster in range(num_clusters):
		print("The centroid for cluster", cluster, "is ", cluster_centroids[cluster])

	total = 0
	for cluster in range(num_clusters):
		num_in_cluster = 0
		temp = []
		for index in range(len(cluster_assignments)):
			if cluster_assignments[index] == cluster:
				num_in_cluster += 1
				temp.append(data[index])
		result.append(temp)
		total += num_in_cluster
		print("Cluster ", cluster, "contains ", num_in_cluster, " addresses.")
	arr = np.array(result)
	if usingNormalizedFeats:
		np.save("Normalized_Cluster_Assignments.npy", arr)
	else:
		np.save("Cluster_Assignments.npy", arr)
	print("Total points was: ", data.shape[0])
	print("We put ", total, " of them into clusters.")


# Loads data from csv into numpy array
# Note that address and rank are not included as features but are added to addr_list
#_______________________________________________

def format_data(usingNormalizedFeats):
	global addr_list
	global training_data
	global normalized_training_data
	result = []
	f_name = training_data
	if (usingNormalizedFeats):
		f_name = normalized_training_data
	with open (f_name, 'rt') as csvfile:
		f_reader = csv.reader(csvfile)
		counter = 0
		for row in f_reader:
			if counter is 0:
				counter = counter + 1
				continue
			addr_list.append((row[0], row[1]))
			row = row[2:]
			float_row = [float(elem) for elem in row]
			result.append(float_row)
	result = np.array(result)
	return result


# Runs scikitlearn's kmeans algorithm
# If you want to seed the random number generator for testing purposes:
#	set random_state = seed in call to KMeans where seed is int with which you wish to seed.
#_______________________________________________

def run_kmeans(data, verbose):
	global num_clusters
	global addr_list
	kmeans = KMeans(n_clusters = num_clusters).fit(data)
	cluster_centroids = kmeans.cluster_centers_
	cluster_assignments = kmeans.labels_

	if verbose:
		for cluster in range(num_clusters):
			print("The centroid for cluster", cluster, "is ", cluster_centroids[cluster])

	return (cluster_centroids, cluster_assignments)


# Compute distortion of centroid assignments returned by KMeans
# Recall from class notes that kmeans can be seen as trying to minimize distortion
# Distortion is just the sum of the L2 norms of the distance between each point and
# the centroid of the cluster to which it is assigned.
#_______________________________________________

def compute_distortion(data, centroids, assignments):
	result = 0.0
	for ex in range(len(data)):
		curr_feats = data[ex]
		curr_centroid = centroids[assignments[ex]]
		result = result + np.linalg.norm(curr_feats - curr_centroid)
	return result


if __name__ == '__main__':
	main()

