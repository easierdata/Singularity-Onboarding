# Tracking the status of onboarding data from Singularity

This notebook serves as a tool for stakeholders to monitor and analyze the progress of onboarding datasets to Filecoin storage providers. Focus on the deal-making progress to aid in decision-making and operational improvements. It utilizes a variety of Python libraries such as pandas for data manipulation, requests for making HTTP requests, matplotlib and seaborn for plotting, and ipywidgets for creating interactive UI elements within the notebook. Here's a step-by-step breakdown of its functionalities and how users can track the status of onboarding data:

1. Data Retrieval: The notebook makes HTTP GET and POST requests to a specified API (BASE_URL) to fetch data related to preparations and deals. This includes information about the pieces in each preparation and the status of deals.
2. Data Processing: After retrieving the data, it processes this information to organize and prepare it for analysis. This involves creating data frames for pieces and deals, and potentially merging or manipulating these data frames for more detailed insights.
3. Visualization: The notebook uses matplotlib and seaborn to create various plots and visualizations. These visualizations help in understanding the distribution and status of preparations and deals. For example, it can show the number of pieces in each preparation, the state of deals, and trends over time.
4. Interactive Widgets: Through ipywidgets, the notebook provides interactive elements, such as buttons or sliders, allowing users to dynamically filter and view the data. This interactivity enhances the user experience by enabling real-time data exploration.
5. Custom Styling: It applies custom styling to plots and interactive tables to improve readability and aesthetics. This includes setting themes, colors, and layout properties.
6. Utility Functions: The notebook includes several utility functions for making HTTP requests, processing data, and creating styled HTML widgets. These functions streamline the workflow and can be reused for different datasets or analyses.
7. Global Variables and Configuration: It defines global variables and configurations, such as the API base URL, color maps for visualization, and style properties for widgets. This centralizes the configuration, making it easier to update or modify.

##### Users can track the status of onboarding data to Filecoin by:

- Running the notebook: Execute the cells in sequence to fetch the latest data, process it, and generate up-to-date visualizations.
- Understand your current work: The provided interactive table to filter and drill down into specific aspects of the data, such as focusing on particular preparations or deal states.
- Track Performance: Study the generated plots to identify trends, patterns, and outliers in the onboarding process. This can help in understanding the efficiency of data onboarding, identifying bottlenecks, and tracking the progress of deals.
