import argparse
import numpy as np
import re
import ast


class MyTransformer(ast.NodeTransformer):
    def visit_Name(self, variable):
        return ast.Name(**{**variable.__dict__, 'id': 'x'})


class Text:
    def __init__(self, text):
        self.text = text

    def remove_comments(self):
        self.text = re.sub(r"'''[\s\S]*'''", "", self.text)
        self.text = re.sub(r""""[\s\S]*""""", "", self.text)

    def remove_variables(self):
        self.text = ast.unparse(MyTransformer().visit(ast.parse(self.text)))

    def prepare_to_antiplagiarism(self):
        self.remove_variables()
        self.remove_comments()



class WorkWithFiles:

    def __init__(self):
        self.args = None
        self.files = []
        self.res = []

    def input_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input')
        parser.add_argument('scores')
        self.args = parser.parse_args()

    def read_args(self):
        self.input_args()
        with open(self.args.input, "r") as input:
            line = input.readline()
            while line != "":
                first, second = line.split()
                with open(first, "r") as first_file, open(second, "r") as second_file:
                    self.files.append((Text(first_file.read()), Text(second_file.read())))
                line = input.readline()

    def write_text(self, lines):
        with open(self.args.scores, "w") as output:
            output.write("\n".join(lines))


class Levenshtein:
    def __init__(self):
        self.help_files = WorkWithFiles()
        self.distances = []
        self.get_Levenshtein_distances()

    @staticmethod
    def get_Levenshtein_distance(first, second):
        n, m = len(first) + 1, len(second) + 1
        matrix = np.zeros((n, m))
        for i in range(n):
            for j in range(m):
                if i == 0 and j == 0:
                    matrix[i][j] = 0
                elif j == 0:
                    matrix[i][j] = i
                elif i == 0:
                    matrix[i][j] = j
                else:
                    matrix[i][j] = min(matrix[i][j - 1] + 1, matrix[i - 1][j] + 1,
                                       matrix[i - 1][j - 1] + int(first[i - 1] != second[j - 1]))
        return round(1 - matrix[n - 1][m - 1] / max(n - 1, m - 1), 2)

    def get_Levenshtein_distances(self):
        self.help_files.read_args()
        for files_pair in self.help_files.files:
            first = files_pair[0]
            first.prepare_to_antiplagiarism()
            second = files_pair[1]
            second.prepare_to_antiplagiarism()
            distance = self.get_Levenshtein_distance(first.text, second.text)
            print(distance)
            self.distances.append(str(distance))
        self.help_files.write_text(self.distances)


if __name__ == '__main__':
    get_Levenshtein_distance = Levenshtein()

