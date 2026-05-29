library(terra)
library(geosphere)
library(tidyverse)
library(windscape)

df <- read.csv("extdata/in_bond_neighbors.csv")

# base wind graph (reuse this!)
wind_base <- rast("extdata/converted.tif") %>%
  wind_series(order = "uuvv") %>%
  wind_rose() %>%
  wind_graph("upwind")
df$node_lon <- df$node_lat
df$node_lat <- df$node_long

df$neigh_lon <- df$neigh_lat
df$neigh_lat <- df$neigh_long

# KEEP ONLY CLEAN COLUMNS
df <- df[, c("node_lon","node_lat","neigh_lon","neigh_lat")]

# distance (you already have this)
df$dist_km <- geosphere::distHaversine(
  cbind(df$node_lon, df$node_lat),
  cbind(df$neigh_lon, df$neigh_lat)
) / 1000

#df <- df[df$dist_km < 50,]

df$wind_time <- NA

nodes <- unique(df[, c("node_lon","node_lat")])

for (i in 1:nrow(nodes)) {
  # make sure wind_base has lon/lat CRS
  terra::crs(wind_base) <- "EPSG:4326"
  
  node <- nodes[i, ]
  
  site_coords <- matrix(
    c(node$node_lon, node$node_lat),
    nrow = 1,
    ncol = 2
  )
  
  site <- terra::vect(
    site_coords,
    type = "points",
    crs = "EPSG:4326"
  )
  
  lc_surface <- least_cost_surface(wind_base, site)
  
  idx <- which(
    abs(df$node_lon - node$node_lon) < 1e-8 &
      abs(df$node_lat - node$node_lat) < 1e-8
  )
  
  if (length(idx) == 0) next
  
  neigh_coords <- as.matrix(
    cbind(df$neigh_lon[idx], df$neigh_lat[idx])
  )
  
  neigh_pts <- terra::vect(
    neigh_coords,
    type = "points",
    crs = "EPSG:4326"
  )
  
  tt <- terra::extract(lc_surface, neigh_pts)
  
  df$wind_time[idx] <- tt[[2]]
}

plot(
  df$dist_km,
  df$wind_time,
  xlab = "Inbound Distance (km)",
  ylab = "Wind Travel Time (hours)",
  pch = 16
)



plot(
  df$dist_km,
  df$wind_time,
#  log = "xy",   # log scale BOTH axes (you can use "y" if only y)
  xlab = "Distance (km)",
  ylab = "Wind Travel Time (hours)",
  pch = 16
#  yaxt = "n"   # we will control labels
)


ggsave(
  "wind_vs_move.png",
  width = 8,
  height = 4,
  dpi = 300
)

library(dplyr)

df <- df[!is.na(df$wind_time), ]

# convert to days if you want consistency
df$wind_time_days <- df$wind_time 

# distance bins
df$dist_class <- cut(
  df$dist_km,
  breaks = c(-Inf, 10, 20, Inf),
  labels = c("0-10 km", "11-20 km", "20+ km")
)

library(dplyr)

df_ccdf <- df %>%
  arrange(wind_time_days) %>%
  group_by(dist_class) %>%
  mutate(
    n = n(),
    rank = row_number(),
    ccdf = 1 - (rank - 1) / n
  )


# =========================
# LIBRARIES
# =========================
library(dplyr)
library(ggplot2)
library(patchwork)
library(scales)

# =========================
# CLEAN + PREP
# =========================
df <- df[!is.na(df$wind_time), ]

df <- df %>%
  mutate(
    wind_time_days = wind_time,
    dist_class = cut(
      dist_km,
      breaks = c(-Inf, 10, 20, Inf),
      labels = c("0-10 km", "11-20 km", "20+ km")
    )
  )

df$dist_class <- factor(df$dist_class,
                        levels = c("0-10 km", "11-20 km", "20+ km"))

# =========================
# LIBRARIES
# =========================
library(dplyr)
library(ggplot2)

# =========================
# CLEAN + PREP
# =========================
df <- df[!is.na(df$wind_time), ]

df <- df %>%
  mutate(
    dist_class = cut(
      dist_km,
      breaks = c(-Inf, 10, 20, Inf),
      labels = c("0-10 km", "11-20 km", "20+ km")
    )
  )

df$dist_class <- factor(df$dist_class,
                        levels = c("0-10 km", "11-20 km", "20+ km"))

# =========================
# CCDF (FULL RANGE, HOURS)
# =========================
df_ccdf <- df %>%
  arrange(wind_time) %>%
  group_by(dist_class) %>%
  mutate(
    n = n(),
    rank = row_number(),
    ccdf = 1 - (rank - 1) / n
  )
# =========================
# PLOT
# =========================
p <- ggplot(df_ccdf,
            aes(x = wind_time, y = ccdf, color = dist_class)) +
  geom_point(size = 1) +
  #scale_x_continuous(
  #  breaks = seq(0, max(df$wind_time, na.rm = TRUE), by = 10)
  #) 
  #scale_x_log10(
  #  breaks = 10^seq(0, 4, by = 1),
  #  labels = scales::trans_format("log10", scales::math_format(10^.x))) +
  scale_y_log10(
    breaks = 10^seq(-4, 0, by = 1),
    labels = scales::trans_format("log10", scales::math_format(10^.x))
  )+
  
  scale_color_manual(values = c(
    "0-10 km" = "#E41A1C",
    "11-20 km" = "#4DAF4A",
    "20+ km" = "#377EB8"
  )) +
  
  labs(
    x = "Wind Travel Time (hours)",
    y = "P(T ≥ t)",
    color = "Distance"
  ) +
  
  
  theme_minimal() +
  theme(
    axis.title = element_text(size = 14),
    axis.text  = element_text(size = 11)
  ) + 
  theme_classic(base_size = 16) +
  theme(
    axis.title = element_text(size = 18),
    axis.text  = element_text(size = 14)
  )
#  scale_x_continuous(
#  breaks = seq(0, max(df$wind_time_days, na.rm = TRUE), by = 1))
  
p

ggsave(
  "ccdf_wind_time.png",
  p,
  width = 16,
  height = 8,
  dpi = 300
)

