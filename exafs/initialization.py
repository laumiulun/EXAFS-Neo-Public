# load the path into dictionary
def loadPaths(ind_options, paths, pathrange, front, end):
    global pathDictionary
    if ind_options == True:
        num_paths = len(paths)
        for i in range(num_paths):
            filename = front + str(paths[i]).zfill(4) + end
            # pathName = 'Path' + str(paths[i])
            pathName = f"Path{paths[i]}"
            pathDictionary.update({pathName: feffdat.feffpath(filename, _larch=mylarch)})
        pathrange = num_paths
    else:
        print(paths)
        for i in range(1, pathrange + 1):
            filename = front + str(i).zfill(4) + end
            # pathName = 'Path'+ str(i)
            pathName = f"Path{i}"
            pathDictionary.update({pathName: feffdat.feffpath(filename, _larch=mylarch)})
            paths = range(1, pathrange + 1)
    return paths, pathrange
