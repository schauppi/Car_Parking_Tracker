import * as webserver from './webserver'
import * as processor from './processor'

processor.initLoop()
webserver.listen()
