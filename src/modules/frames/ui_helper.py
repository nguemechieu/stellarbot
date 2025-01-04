from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLayout, QStyle


def create_label(text, style, layout):
    """
    Create a QLabel with the given text and style.

    Args:
    text (str): The text to display on the label.
    style (str): The style sheet for the label.

    Returns:
    QLabel: The created QLabel.
    """
    label = QtWidgets.QLabel(text, layout)
    label.setStyleSheet(style)
    layout.addWidget(label)
    layout.addSpacing(20)

    return label


def create_input_field(label_text, style, layout):
    """
    Create a QLineEdit with the given label text and style.

    Args:
    label_text (str): The text to display on the label.
    style (str): The style sheet for the label.

    Returns:
    QLineEdit: The created QLineEdit.
    """
    label = QtWidgets.QLabel(label_text, layout)
    layout.addWidget(label)

    input_field = QtWidgets.QLineEdit(layout)
    input_field.setStyleSheet(style)
    layout.addWidget(input_field)
    layout.addSpacing(20)

    return input_field



def create_button(text, style, layout):
    """
    Create a QPushButton with the given text and style.

    Args:
    text (str): The text to display on the button.
    style (str): The style sheet for the button.

    Returns:
    QPushButton: The created QPushButton.
    """
    button = QtWidgets.QPushButton(text, layout)
    button.setStyleSheet(style)
    layout.addWidget(button)
    layout.addSpacing(20)

    return button



def create_checkbox(text, style, layout):
    """
    Create a QCheckBox with the given text and style.

    Args:
    text (str): The text to display on the checkbox.
    style (str): The style sheet for the checkbox.

    Returns:
    QCheckBox: The created QCheckBox.
    """
    checkbox = QtWidgets.QCheckBox(text, layout)
    checkbox.setStyleSheet(style)
    layout.addWidget(checkbox)
    layout.addSpacing(20)

    return checkbox

def create_dropdown(options, style, layout):
    """
    Create a QComboBox with the given options and style.

    Args:
    options (list): A list of options for the dropdown.
    style (str): The style sheet for the dropdown.

    Returns:
    QComboBox: The created QComboBox.
    """
    dropdown = QtWidgets.QComboBox(layout)
    dropdown.addItems(options)
    dropdown.setStyleSheet(style)
    layout.addWidget(dropdown)
    layout.addSpacing(20)

    return dropdown
from PyQt5.QtWidgets import QLabel, QVBoxLayout
import pandas as pd

def create_label_df(df: pd.DataFrame, layout: QVBoxLayout) -> None:
    """
    Create and display labels based on the contents of the provided DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        layout (QVBoxLayout): The layout to which the labels will be added.
    """
    # Ensure the DataFrame contains the required column
    if 'total_daily_portfolio_value_change' not in df.columns:
        raise ValueError("The DataFrame must contain a 'total_daily_portfolio_value_change' column.")

    # Iterate through the DataFrame rows
    for index, row in df.iterrows():
        # Construct label text
        try:
            row_text = ', '.join([f'{col}: {row[col]}' for col in df.columns])
        except KeyError as e:
            raise KeyError(f"Error processing row {index}: Missing column - {str(e)}")

        label_text = f"Row {index}: {row_text}"

        # Create QLabel
        label = QLabel(label_text)

        # Determine background color based on value
        total_change = row['total_daily_portfolio_value_change']
        color = "blue" if total_change > 0 else "red"

        # Set QLabel style
        label.setStyleSheet(
            f"""
            color: white;
            font-size: 14px;
            background-color: {color};
            padding: 5px;
            """
        )

        # Add QLabel to the layout
        layout.addWidget(label)


def create_radio_buttons(options, style, layout):
    """
    Create a group of QRadioButtons with the given options and style.

    Args:
    options (list): A list of options for the radio buttons.
    style (str): The style sheet for the radio buttons.

    Returns:
    list: A list of created QRadioButtons.
    """
    radio_buttons = []
    for option in options:
        radio_button = QtWidgets.QRadioButton(option, layout)
        radio_button.setStyleSheet(style)
        layout.addWidget(radio_button)
        radio_buttons.append(radio_button)
        layout.addSpacing(10)

    return radio_buttons

def create_frame(title, style, layout):
    """
    Create a QFrame with the given title and style.

    Args:
    title (str): The title for the frame.
    style (str): The style sheet for the frame.

    Returns:
    QFrame: The created QFrame.
    """
    frame = QtWidgets.QFrame(layout)
    frame.setStyleSheet(style)
    layout.addWidget(frame)

    title_label = QtWidgets.QLabel(title, frame)
    title_label.setStyleSheet("font-weight: bold; font-size: 20px;")
    frame.setLayout(QtWidgets.QVBoxLayout())
    frame.layout().addWidget(title_label)

    return frame

def create_group_box(title, style, layout):
    """
    Create a QGroupBox with the given title and style.

    Args:
    title (str): The title for the group box.
    style (str): The style sheet for the group box.

    Returns:
    QGroupBox: The created QGroupBox.
    """
    group_box = QtWidgets.QGroupBox(title, layout)
    group_box.setStyleSheet(style)
    layout.addWidget(group_box)

    group_box_layout = QtWidgets.QVBoxLayout(group_box)
    group_box_layout.setContentsMargins(0, 0, 0, 0)

    return group_box_layout

def create_scroll_area(layout):
    """
    Create a QScrollArea with a vertical layout.

    Args:
    layout (QVBoxLayout): The layout for the scroll area.

    Returns:
    QScrollArea: The created QScrollArea.
    """
    scroll_area = QtWidgets.QScrollArea(layout)
    scroll_area.setWidgetResizable(True)

    scroll_area_layout = QtWidgets.QVBoxLayout(scroll_area.widget())
    scroll_area_layout.setContentsMargins(0, 0, 0, 0)

    return scroll_area, scroll_area_layout

def create_table(headers, data, style, layout):
    """
    Create a QTableWidget with the given headers, data, and style.

    Args:
    headers (list): A list of headers for the table.
    data (list): A list of lists representing the data for the table.
    style (str): The style sheet for the table.
    layout (QVBoxLayout): The layout for the table.

    Returns:
    QTableWidget: The created QTableWidget.
    """
    table = QtWidgets.QTableWidget(len(data), len(headers), layout)
    table.setVerticalHeaderLabels(headers)
    table.setStyleSheet(style)

    for i, row in enumerate(data):
        for j, cell_data in enumerate(row):
            table.setItem(i, j, QtWidgets.QTableWidgetItem(str(cell_data)))

    layout.addWidget(table)

    return table

def create_line_edit(text, style, layout):
    """
    Create a QLineEdit with the given text and style.

    Args:
    text (str): The initial text for the line edit.
    style (str): The style sheet for the line edit.
    layout (QVBoxLayout): The layout for the line edit.

    Returns:
    QLineEdit: The created QLineEdit.
    """
    line_edit = QtWidgets.QLineEdit(text, layout)
    line_edit.setStyleSheet(style)

    return line_edit

def create_text_area(text, style, layout):
    """
    Create a QTextEdit with the given text and style.

    Args:
    text (str): The initial text for the text area.
    style (str): The style sheet for the text area.
    layout (QVBoxLayout): The layout for the text area.

    Returns:
    QTextEdit: The created QTextEdit.
    """
    text_area = QtWidgets.QTextEdit(text, layout)
    text_area.setStyleSheet(style)

    return text_area

def create_horizontal_line(layout: QLayout=None):
    """
    Create a horizontal line with the default style.

    Args:
    layout (QVBoxLayout): The layout for the horizontal line.

    Returns:
    QFrame: The created horizontal line.
    """
    line = QtWidgets.QFrame(layout)
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    layout.addWidget(line)

    return line

def create_vertical_line(layout: QLayout=None):
    """
    Create a vertical line with the default style.

    Args:
    layout (QVBoxLayout): The layout for the vertical line.

    Returns:
    QFrame: The created vertical line.
    """
    line = QtWidgets.QFrame(layout)
    line.setFrameShape(QtWidgets.QFrame.VLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    layout.addWidget(line)

    return line

def create_progress_bar(maximum_range=100, style:QStyle=None, layout:QLayout=None):
    """
    Create a QProgressBar with the given maximum value and style.

    Args:
    maximum (int): The maximum value for the progress bar.
    style (str): The style sheet for the progress bar.
    layout (QVBoxLayout): The layout for the progress bar.

    Returns:
    QProgressBar: The created QProgressBar.
    """
    progress_bar = QtWidgets.QProgressBar(layout)
    progress_bar.setRange(0, maximum_range)
    progress_bar.setStyleSheet(style)
    layout.addWidget(progress_bar)

    return progress_bar

def create_slider(minimum, maximum, value, style, layout):
    """
    Create a QSlider with the given minimum, maximum, and initial value and style.

    Args:
    minimum (int): The minimum value for the slider.
    maximum (int): The maximum value for the slider.
    value (int): The initial value for the slider.
    style (str): The style sheet for the slider.
    layout (QVBoxLayout): The layout for the slider.

    Returns:
    QSlider: The created QSlider.
    """
    slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, layout)
    slider.setRange(minimum, maximum)
    slider.setValue(value)
    slider.setStyleSheet(style)

    return slider

def create_spin_box(minimum, maximum, value, style, layout):
    """
    Create a QSpinBox with the given minimum, maximum, and initial value and style.

    Args:
    minimum (int): The minimum value for the spin box.
    maximum (int): The maximum value for the spin box.
    value (int): The initial value for the spin box.
    style (str): The style sheet for the spin box.
    layout (QVBoxLayout): The layout for the spin box.

    Returns:
    QSpinBox: The created QSpinBox.
    """
    spin_box = QtWidgets.QSpinBox(layout)
    spin_box.setRange(minimum, maximum)
    spin_box.setValue(value)
    spin_box.setStyleSheet(style)

    return spin_box

def create_color_picker(style, layout):
    """
    Create a QColorDialog for selecting a color and style it.

    Args:
    style (str): The style sheet for the color picker.
    layout (QVBoxLayout): The layout for the color picker.

    Returns:
    QColorDialog: The created QColorDialog.
    """
    color_dialog = QtWidgets.QColorDialog(layout)
    color_dialog.setStyleSheet(style)

    return color_dialog

def create_file_dialog(dialog_type, style, layout):
    """
    Create a QFileDialog for selecting a file or directory and style it.

    Args:
    dialog_type (str): The type of the file dialog (e.g., "open", "save").
    style (str): The style sheet for the file dialog.
    layout (QVBoxLayout): The layout for the file dialog.

    Returns:
    QFileDialog: The created QFileDialog.
    """
    file_dialog = QtWidgets.QFileDialog(layout)
    file_dialog.setStyleSheet(style)
    file_dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)

    if dialog_type == "open":
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
    elif dialog_type == "save":
        file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)

    return file_dialog

def create_message_box(title, message, buttons, style, layout):
    """
    Create a QMessageBox with the given title, message, buttons, icon, and style.

    Args:
    title (str): The title for the message box.
    message (str): The message for the message box.
    buttons (list): A list of button labels for the message box.
    icon (str): The icon for the message box (e.g., "information", "warning", "critical").
    style (str): The style sheet for the message box.
    layout (QVBoxLayout): The layout for the message box.

    Returns:
    QMessageBox: The created QMessageBox.
    """
    message_box = QtWidgets.QMessageBox(layout)
    message_box.setWindowTitle(title)
    message_box.setText(message)
    message_box.setStandardButtons(getattr(QtWidgets.QMessageBox, buttons[0]))
    for button in buttons[1:]:
        message_box.addButton(getattr(QtWidgets.QMessageBox, button), getattr(QtWidgets.QMessageBox, button))
        message_box.button(button).setStyleSheet(style)


    return message_box

def create_radio_button(text, style, layout):
    """
    Create a QRadioButton with the given text and style.

    Args:
    text (str): The text for the radio button.
    style (str): The style sheet for the radio button.
    layout (QVBoxLayout): The layout for the radio button.

    Returns:
    QRadioButton: The created QRadioButton.
    """
    radio_button = QtWidgets.QRadioButton(text, layout)
    radio_button.setStyleSheet(style)

    return radio_button

