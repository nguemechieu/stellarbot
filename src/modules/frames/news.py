from PyQt5.QtWidgets import QFrame, QVBoxLayout, QGridLayout, QLabel
from src.modules.engine.engine_helper import get_news_data


class NewsFrame(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the News widget."""
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(100, 100, 1530, 780)
        self.df = get_news_data()

        self.controller.logger.info("News widget initialized"+self.df)
        self.setWindowTitle("News")

        # Create widgets to display the news information
        self.create_widgets()

    def create_widgets(self):
        """Create and arrange widgets."""
        layout = QVBoxLayout()
        label_title = QLabel("News", self)
        layout.addWidget(label_title)

        # Create a grid layout to arrange the news data
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        # Add news data to the grid layout
        for i, (index, row) in enumerate(self.df.iterrows()):
            # Create labels for each column
            labels = [QLabel(text=str(value), parent=self) for value in row]

            # Add labels to the grid layout
            for col_idx, label in enumerate(labels):
                grid_layout.addWidget(label, i, col_idx)

                # Set the maximum width of the labels to fit the width of the grid
                label.setWordWrap(True)

            # Style the first column (title)
            labels[0].setStyleSheet("font-size: 18px; font-weight: bold; background-color: #F8F9FA; "
                                    "border-bottom: 1px solid #E9ECEF; padding: 10px;")

            # Style the other columns
            for label in labels[1:]:
                label.setStyleSheet("font-size: 14px; background-color: #FFFFFF; "
                                    "border-bottom: 1px solid #E9ECEF; padding: 5px;")

            # Add a spacer row between news items
            grid_layout.addItem(QLabel(), i + 1, 0)

        self.setLayout(layout)
