for i in range(9):
            for j in range(9):
                if self.puzzle[i][j] != 0:
                    self.fixed_cells.add((i, j))   