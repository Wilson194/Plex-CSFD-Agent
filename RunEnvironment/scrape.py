import urllib2

with open('com.plexapp.agents.dataget.log') as f:
    lines = f.readlines()

with open('data', 'w') as f:
    for line in lines:
        if '==>' in line:
            data = line.split('==>')[1]
            data = urllib2.unquote(data)

            path, name, year, length = data.split(';')

            f.write(data)
