library(windscape)
library(tidyverse)
library(terra)
library(geosphere)
library(viridis)

system.file("extdata", package = "windscape")
list.files(system.file("extdata", package = "windscape"))
wind <- rast("extdata/converted.tif")

## hub_lat,hub_long is slighlty
## different from the one in the figure
hub_lat = 176
hub_long = -39

site <- vect(matrix(c(hub_lat,hub_long), 1)) # lat-lon coordinates of a focal site

lc <- rast("extdata/converted.tif") %>% # load wind time series rasters
  wind_series(order = "uuvv") %>% # convert to a formal wind field time series object
  wind_rose() %>% # summarize into wind rose conductance object
  wind_graph("upwind") %>% # format as connectivity graph
  least_cost_surface(site) # calculate least cost path from coordinates
# define extent: xmin, xmax, ymin, ymax
e <- ext(175, 179, -41, -37)
par(mar = c(6, 6, 4, 2))  # bottom, left, top, right

png("wind_inbound_travel_time_zoom.png", width = 1800, height = 1200, res = 200)

r_crop <- crop(lc, e)
#r_fine <- disagg(r_crop, fact = 4)  # 4x finer resolution

plot(r_crop,axes = FALSE,xlab="Longitude",ylab="Latitude",asp = 1,col = rev(hcl.colors(50, "inferno")),plg = list(title = "Wind Travel Time",
                                                                                                                  cex = 1.2)) # plot map of travel times
contour(r_crop, add = TRUE,axes = FALSE,xaxt = "n", yaxt = "n")

neighbor_values = read.csv("extdata/hub_neigh_ids.csv")

hub <- c(hub_lat,hub_long)
# hub = c(lat, lon)
hub_pt <- vect(
  matrix(c(hub[2], hub[1]), ncol = 2),  # (lon, lat)
  crs = "EPSG:4326"
)



neighbor_values$dist <- distHaversine(hub,cbind(neighbor_values$lon,neighbor_values$lat))
neighbor_values$dist <- neighbor_values$dist / 1000
for (i in 1:nrow(neighbor_values)){
  lat <- neighbor_values$lat[i]
  long <- neighbor_values$long[i]
  neigh_site <- vect(matrix(c(long , lat), 1)) # lat-lon coordinates of a focal site
  points(neigh_site, col = neighbor_values$dist,xaxt = "n", yaxt = "n") # add origin location to map
}
points(site, col = "red",xaxt = "n", yaxt = "n") # add origin location to map
dev.off()
# Create all points at once
neigh_sites <- vect(cbind(neighbor_values$lon, neighbor_values$lat))

# Extract travel time from raster
travel_time_vals <- terra::extract(lc, neigh_sites)
neighbor_values$travel_time <- travel_time_vals[,2]

# Plot relationship (THIS is your real result)
plot(
  neighbor_values$dist,
  neighbor_values$travel_time,
  xlab = "Geodesic Distance (km)",
  ylab = "Wind Travel Time (hours)",
  pch = 16
)
png("wind_inbound_travel_time_zoom.png", width = 1800, height = 1200, res = 200)

# Focal node / hub
hub <- c(hub_lat,hub_long) # lon, lat
site <- vect(matrix(hub, ncol = 2), crs = "EPSG:4326")

# Wind least-cost surface
lc <- rast("extdata/converted.tif") %>%
  wind_series(order = "uuvv") %>%
  wind_rose() %>%
  wind_graph("upwind") %>%
  
  least_cost_surface(site)

# Optional: convert hours to days
# lc <- lc / 24
example_rose <- rast("extdata/converted.tif") %>%
  wind_series(order = "uuvv") %>%
  wind_rose()
neighbor_values <- read.csv("extdata/hub_neigh_ids.csv")

# Make sure longitude column is consistently named
if ("long" %in% names(neighbor_values) && !"lon" %in% names(neighbor_values)) {
  neighbor_values$lon <- neighbor_values$long
}

neighbor_values$dist_km <- distHaversine(
  hub,
  cbind(neighbor_values$lon, neighbor_values$lat)
) / 1000

# Zoom around focal node
zoom_deg <- 2.0   # try 1.5 if you want tighter
zoom_ext <- ext(
  hub[1] - zoom_deg, hub[1] + zoom_deg,
  hub[2] - zoom_deg, hub[2] + zoom_deg
)

lc_zoom <- crop(lc, zoom_ext)

# Neighbor points
neigh_sites <- vect(
  cbind(neighbor_values$lon, neighbor_values$lat),
  crs = "EPSG:4326"
)



plot(
  lc_zoom,
  col = viridis(100, option = "inferno", direction = -1),
  main = "",
  axes = FALSE,
  
  plg = list(title = "Wind travel time (hours)")
)

contour(
  lc_zoom,
  add = TRUE,
  col = "black",
  lwd = 0.6,
  drawlabels = TRUE,
  labcex = 0.7
)

points(
  neigh_sites,
  pch = 21,
  bg = "white",
  col = "black",
  cex = 0.7
)

points(
  site,
  pch = 21,
  bg = "red",
  col = "black",
  cex = 1.7,
  lwd = 1.2
)


#  title(xlab = "Longitude (°E)", ylab = "Latitude (°S)")
# Save publication-style supplementary map
dev.off()
# lines(lowess(neighbor_values$dist, neighbor_values$travel_time), col = "blue", lwd = 2)

