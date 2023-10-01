output = []

for i in range(1, 101):
  count = 0
  for j in range (1, i + 1):
    if (i%j==0):
      count += 1
  output.append([i, count, round(count/i, 2)])

output.sort(reverse=True, key=lambda x: x[2])

for elem in output:
  print(elem)