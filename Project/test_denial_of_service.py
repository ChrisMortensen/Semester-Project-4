import time
import random as rand
from collections import deque
from denial_of_service import is_rate_limited

def write_latex_table(durations, avg_time, max_time, output_file="rate_limiter_results.tex"):
    total_msgs = len(durations)
    columns = 4

    with open(output_file, 'w') as f:
        f.write("\\begin{table}[H]\n")
        f.write("\\centering\n")

        # Header
        f.write("\\begin{tabular}{" + "|c|c|" * columns + "}\n")
        f.write("\\hline\n")
        f.write(" & ".join(["\\textbf{Msg \#} & \\textbf{Time (ms)}"] * columns) + " \\\\\n")
        f.write("\\hline\n")

        # Rows
        rows = (total_msgs + columns - 1) // columns  # Ceiling division
        for row in range(rows):
            line = ""
            for col in range(columns):
                index = row + rows * col
                if index < total_msgs:
                    msg_number = index + 1  # Start from 1 instead of 0
                    line += f"{msg_number:02d} & {durations[index] * 1000:.4f} "
                else:
                    line += " & "  # Empty cell pair
                if col < columns - 1:
                    line += "& "
            f.write(line + "\\\\\n")

        f.write("\\hline\n")
        f.write(f"\\multicolumn{{{columns * 2}}}{{|c|}}{{\\textbf{{Average Time: {avg_time * 1000:.4f} ms}} "
                f"\\quad \\textbf{{Max Time: {max_time * 1000:.4f} ms}}}} \\\\\n")
        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write(f"\\caption{{Rate Limiter Performance Test for {total_msgs} Messages}}\n")
        f.write("\\end{table}\n")

    print(f"LaTeX output written to {output_file}")

def test_rate_limiter_performance(max_msgs_per_sec=5, total_msgs=100):
	timestamps = deque()
	durations = []

	for _ in range(total_msgs):
		start = time.perf_counter()
		is_rate_limited(timestamps, max_msgs_per_sec)
		end = time.perf_counter()
		durations.append(end - start)

		# Simulate actual time passing
		time.sleep(rand.randint(1,50)/1000) # 1 to 50 ms between messages

	avg_time = sum(durations) / total_msgs
	max_time = max(durations)
     
	# Write LaTeX table to file
	write_latex_table(durations, avg_time, max_time)

if __name__ == "__main__":
	test_rate_limiter_performance()
