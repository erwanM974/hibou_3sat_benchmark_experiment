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
  # ==============================================
  report <- read.table(file=file_path, 
                       header = FALSE, 
                       sep = ",",
                       blank.lines.skip = TRUE, 
                       fill = TRUE)
  
  names(report) <- as.matrix(report[1, ])
  report <- report[-1, ]
  report[] <- lapply(report, function(x) type.convert(as.character(x)))
  report
}
# ==============================================


geom_ptsize = 1
geom_stroke = 1
geom_shape = 19

make_plot_diagram <- function(report_file_str,plot_title_str) {
  report_data <- read_sat_report(report_file_str)
  
  g <- ggplot(report_data, aes(x=varisat_time, y=hibou_time, color=varisat_res)) +
    geom_point(size = geom_ptsize, stroke = geom_stroke, shape = geom_shape) + 
    labs(colour = "isSAT", x = "varisat time", y = "hibou time") +
    ggtitle(plot_title_str) +
    theme(plot.title = element_text(margin = margin(b = -25)),
          axis.title.x = element_text(margin = margin(t = 5)),
          axis.title.y = element_text(margin = margin(r = 5)))
  g
  (g + scale_color_manual(values=c("False" = "red", "True" = "blue")))
}

make_plot_diagram("./satbenchmark_hibou/sat_membership_experiment_mahe.csv", 
                  "Custom")

make_plot_diagram("./satbenchmark_hibou/sat_membership_experiment_uf20.csv",
                  "UF20")

uf20 <- read_sat_report("./satbenchmark_hibou/sat_membership_experiment_uf20.csv")

mean(uf20$hibou_time)
mean(uf20$varisat_time)
max(uf20$hibou_time)
summary(uf20$varisat_time)
summary(uf20$hibou_time)
sd(uf20$varisat_time)
sd(uf20$hibou_time)

