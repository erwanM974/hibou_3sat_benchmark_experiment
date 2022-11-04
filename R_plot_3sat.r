#
# Copyright 2022 Erwan Mahe (github.com/erwanM974)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

rm(list=ls())
# ==============================================
library(ggplot2)
library(scales)
# ==============================================

# ==============================================
read_sat_report <- function(file_path) {
  # ===
  report <- read.table(file=file_path, 
                       header = FALSE, 
                       sep = ";",
                       blank.lines.skip = TRUE, 
                       fill = TRUE)
  
  names(report) <- as.matrix(report[1, ])
  report <- report[-1, ]
  report[] <- lapply(report, function(x) type.convert(as.character(x)))
  report
}
# ==============================================


# ==============================================
geom_ptsize = 1
geom_stroke = 1
geom_shape = 19
# ===
draw_scatter_splot <- function(report_data,plot_title_str,is_log_scale) {
  g <- ggplot(report_data, aes(x=varisat_time_median, y=hibou_time_median, color=varisat_result))
  # 
  if (is_log_scale) {
    g <- g + scale_y_continuous(trans='log10') + scale_x_continuous(trans='log10')
  }
  #
  g <- g + geom_point(size = geom_ptsize, stroke = geom_stroke, shape = geom_shape) + 
    labs(colour = "isSAT", x = "varisat time", y = "hibou time") +
    ggtitle(plot_title_str) +
    theme(plot.title = element_text(margin = margin(b = -25)),
          axis.title.x = element_text(margin = margin(t = 5)),
          axis.title.y = element_text(margin = margin(r = 5))) +
    scale_color_manual(values=c("False" = "red", "True" = "blue"))
  #
  g
}
# ==============================================


# ==============================================
treat_benchmark_data <- function(file_path,benchmark_name,is_log_scale) {
  bench_data <- read_sat_report(file_path)
  
  print("")
  print(benchmark_name)
  print("varisat")
  print(summary(bench_data$varisat_time_median))
  print(sd(bench_data$varisat_time_median))
  print("hibou")
  print(summary(bench_data$hibou_time_median))
  print(sd(bench_data$hibou_time_median))
  print("")
  
  plot_title <- benchmark_name
  if (is_log_scale) {
    plot_title <- paste(benchmark_name, "(log scale)", sep=" ")
  }
  
  bench_plot <- draw_scatter_splot(bench_data,plot_title,is_log_scale)
  
  plot_file_name <- paste(gsub(" ", "_", benchmark_name), "png", sep=".")
  
  ggsave(plot_file_name, bench_plot, width = 2000, height = 1500, units = "px")
}
# ==============================================

