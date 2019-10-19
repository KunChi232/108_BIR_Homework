def minEditDist(sm,sn):
  m,n = len(sm),len(sn)
  D = map(lambda y: map(lambda x,y : y if x==0 else x if y==0 else 0,
    range(n+1),[y]*(n+1)), range(m+1))
  for i in range(1,m+1):
    for j in range(1,n+1):
      D[i][j] = min( D[i-1][j]+1, D[i][j-1]+1, 
        D[i-1][j-1] + apply(lambda: 0 if sm[i-1] == sn[j-1] else 2)) 
  for i in range(0,m+1):
    print D[i] 
  return D[m][n] 