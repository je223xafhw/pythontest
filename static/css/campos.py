# temporary file to past all the possivle positions of the animals in a csv file
# not needed when i just javascript
f = open("campositions.css", "w")
f.write("")
f.close()
f = open("campositions.css", "a")
for m in range(0, 700):
    for n in range(0, 700):
        string = '.camcontainer .cam' + \
            str(m) + '_' + str(n) + '{\n margin-left: ' + str(m) + \
            'px;\n margin-top: ' + str(n) + 'px;\n}\n\n'
        f.write(string)

f.close()
