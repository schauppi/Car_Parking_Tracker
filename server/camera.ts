import * as childProcess from 'child_process'
import * as path from 'path'
import * as dotenv from 'dotenv'

dotenv.config({
  path: path.join(__dirname, '../.env')
})


const LEFT_CAMERA_STREAM_URL = process.env.LEFT_CAMERA_STREAM_URL
const RIGHT_CAMERA_STREAM_URL = process.env.RIGHT_CAMERA_STREAM_URL
const FILE_DIRECTORY = path.join(__dirname, '../data/raw')

if (!LEFT_CAMERA_STREAM_URL) {
  throw new Error('Environment Variable "LEFT_CAMERA_STREAM_URL" not provided')
}
if (!RIGHT_CAMERA_STREAM_URL) {
  throw new Error('Environment Variable "RIGHT_CAMERA_STREAM_URL" not provided')
}

function takePicture (streamUrl: string, filename: string): Promise<string> {
  const filepath = path.join(FILE_DIRECTORY, filename)
  const execCommand = `ffmpeg -rtsp_transport tcp -ss 2 -i ${streamUrl} -y -f image2 -qscale 0 -frames 1 ${filepath}`

  return new Promise((resolve, reject) => {
    childProcess.exec(execCommand, (err, stdout) => {
      if (err) {
        reject(err)
      } else {
        resolve(stdout)
      }
    })
  })
}

export function snapshot (timestamp: number | string): Promise<[string, string]> {
  const baseName = timestamp + '__'
  const leftFilename = baseName + 'left.jpg'
  const rightFilename = baseName + 'right.jpg'

  return Promise.all([
    takePicture(LEFT_CAMERA_STREAM_URL, leftFilename),
    takePicture(RIGHT_CAMERA_STREAM_URL, rightFilename)
  ])
}
