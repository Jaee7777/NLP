import pandas as pd


def load_data(file_path):
    """Load data from a CSV file into a pandas DataFrame."""
    return pd.read_csv(file_path)


if __name__ == "__main__":
    data = load_data("../data/dataset_OH_label.csv")

    n = 0
    print(data["full_text"][n])
    print(data["manual_label"][n])

    # data["manual_label"][n] = "chinese"
    # data.to_csv("../data/dataset_OH_label.csv", index=False)

    data_output = data[["page_id", "assigned_to", "manual_label"]]
    data_output.to_csv("../data/manual_labels_OH.csv", index=False)
