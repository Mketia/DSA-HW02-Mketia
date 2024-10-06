import os
import re  # Import the regex module for pattern matching

class SparseMatrix:
    """
    Represents a sparse matrix using a dictionary to store non-zero elements.
    """

    def __init__(self, row_count, col_count):
        self.row_count = row_count  # Total number of rows
        self.col_count = col_count  # Total number of columns
        self.data = {}  # Dictionary to store non-zero elements

    @classmethod
    def from_file(cls, file_path):
        """
        Creates a SparseMatrix instance from a specified file.
        
        :param file_path: The path to the matrix file.
        :return: An instance of SparseMatrix.
        """
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()

            if len(lines) < 2:
                raise ValueError(
                    f"The file {file_path} does not have enough lines for matrix dimensions."
                )

            # Extract matrix dimensions
            row_pattern = re.match(r'rows=(\d+)', lines[0].strip())  # Match row format
            col_pattern = re.match(r'cols=(\d+)', lines[1].strip())  # Match column format

            if not row_pattern or not col_pattern:
                raise ValueError(
                    f"Invalid format in file {file_path}. Expected 'rows=X' and 'cols=Y'."
                )

            total_rows = int(row_pattern[1])
            total_cols = int(col_pattern[1])

            sparse_matrix = cls(total_rows, total_cols)

            # Parse non-zero entries
            for i in range(2, len(lines)):
                line = lines[i].strip()
                if line == "":
                    continue  # Skip any empty lines

                entry_pattern = re.match(r'\((\d+),\s*(\d+),\s*(-?\d+)\)', line)
                if not entry_pattern:
                    raise ValueError(
                        f"Invalid format at line {i + 1} in file {file_path}: {line}"
                    )

                row = int(entry_pattern[1])
                col = int(entry_pattern[2])
                value = int(entry_pattern[3])

                sparse_matrix.set_element(row, col, value)

            return sparse_matrix
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise e

    def get_element(self, row_idx, col_idx):
        """
        Retrieves the value at a specific position in the matrix.

        :param row_idx: Row index of the desired element.
        :param col_idx: Column index of the desired element.
        :return: Value at the specified position, or 0 if not set.
        """
        key = (row_idx, col_idx)
        return self.data.get(key, 0)  # Return the value or 0 if not found

    def set_element(self, row_idx, col_idx, value):
        """
        Sets the value at a specific position in the matrix.

        :param row_idx: Row index where the value should be set.
        :param col_idx: Column index where the value should be set.
        :param value: The value to assign at the specified position.
        """
        if row_idx >= self.row_count:
            self.row_count = row_idx + 1  # Update row count if necessary
        if col_idx >= self.col_count:
            self.col_count = col_idx + 1  # Update column count if necessary

        key = (row_idx, col_idx)
        self.data[key] = value  # Assign the value to the dictionary

    def add(self, other_matrix):
        """
        Adds another sparse matrix to this one.

        :param other_matrix: The SparseMatrix to add.
        :return: A new SparseMatrix that is the result of the addition.
        """
        if self.row_count != other_matrix.row_count or self.col_count != other_matrix.col_count:
            raise ValueError("Matrices must have the same dimensions for addition.")

        result_matrix = SparseMatrix(self.row_count, self.col_count)

        # Add elements from the first matrix
        for (row, col), val in self.data.items():
            result_matrix.set_element(row, col, val)

        # Add elements from the second matrix
        for (row, col), val in other_matrix.data.items():
            current_val = result_matrix.get_element(row, col)
            result_matrix.set_element(row, col, current_val + val)

        return result_matrix

    def subtract(self, other_matrix):
        """
        Subtracts another sparse matrix from this one.

        :param other_matrix: The SparseMatrix to subtract.
        :return: A new SparseMatrix that is the result of the subtraction.
        """
        if self.row_count != other_matrix.row_count or self.col_count != other_matrix.col_count:
            raise ValueError("Matrices must have the same dimensions for subtraction.")

        result_matrix = SparseMatrix(self.row_count, self.col_count)

        # Subtract elements from the second matrix from the first matrix
        for (row, col), val in self.data.items():
            result_matrix.set_element(row, col, val)

        for (row, col), val in other_matrix.data.items():
            current_val = result_matrix.get_element(row, col)
            result_matrix.set_element(row, col, current_val - val)

        return result_matrix

    def multiply(self, other_matrix):
        """
        Multiplies this sparse matrix with another.

        :param other_matrix: The SparseMatrix to multiply.
        :return: A new SparseMatrix that is the result of the multiplication.
        """
        if self.col_count != other_matrix.row_count:
            raise ValueError("Number of columns of the first matrix must equal the number of rows of the second matrix.")

        result_matrix = SparseMatrix(self.row_count, other_matrix.col_count)

        # Perform multiplication
        for (row, col), val in self.data.items():
            for k in range(other_matrix.col_count):
                other_val = other_matrix.get_element(col, k)
                if other_val != 0:
                    current_val = result_matrix.get_element(row, k)
                    result_matrix.set_element(row, k, current_val + val * other_val)

        return result_matrix

    def __str__(self):
        """
        Provides a string representation of the SparseMatrix.

        :return: A formatted string showing the matrix's non-zero elements.
        """
        output = f"rows={self.row_count}\ncols={self.col_count}\n"
        for key, val in self.data.items():
            output += f"({key[0]}, {key[1]}, {val})\n"
        return output.strip()  # Return trimmed string

    def save_to_file(self, output_path):
        """
        Saves the SparseMatrix to a specified file.

        :param output_path: The path to save the matrix file.
        """
        content = str(self)  # Get the string representation
        with open(output_path, "w") as file:
            file.write(content)  # Write to the output file

def perform_calculations():
    """
    Manages user input for matrix operations and executes the selected operation.
    """
    try:
        # Define operations 
        operations = {
            '1': {"name": "subtraction", "method": "subtract"},
            '2': {"name": "multiplication", "method": "multiply"},
            '3': {"name": "addition", "method": "add"},
        }

        # Display the operations menu
        print("Available operations:")
        for key, op in operations.items():
            print(f"{key}: {op['name']}")

        first_matrix_path = input("Enter the file path for the first matrix: ")
        matrix1 = SparseMatrix.from_file(first_matrix_path)
        print("1st matrix loaded successfully.\n")

        second_matrix_path = input("Enter the file path for the second matrix: ")
        matrix2 = SparseMatrix.from_file(second_matrix_path)
        print("2nd matrix loaded successfully.\n")

        operation_choice = input("Choose an operation (1, 2, or 3): ")
        selected_operation = operations.get(operation_choice)

        if not selected_operation:
            raise ValueError("Invalid operation choice.")

        result_matrix = getattr(matrix1, selected_operation["method"])(matrix2)
        print(f"Output of {selected_operation['name']} operation:\n{result_matrix}")

        # Automatically save the result to a file named "result.txt"
        output_file_path = "result.txt"
        result_matrix.save_to_file(output_file_path)
        print(f"Output file saved at: {output_file_path}")

    except Exception as error:
        print("Error:", error)

# Execute the matrix operation function
perform_calculations()