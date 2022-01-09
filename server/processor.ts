import * as dotenv from 'dotenv'
import * as childProcess from 'child_process'
import * as path from 'path'
import * as dayjs from 'dayjs'
import * as camera from './camera'

dotenv.config({
  path: path.join(__dirname, '../.env')
})

const LOOP_TIMEOUT = parseInt(process.env.LOOP_TIMEOUT || '5000')
const PYTHON_EXECUTOR = path.resolve(process.env.PYTHON_PATH) || 'py'
const PYTHON_CWD = path.join(__dirname, '../processor')

function processSnapshot (leftFilename: string, rightFilename: string, stitchedFilename: string, outputFilename: string): Promise<any> {
  const execCommand = `${PYTHON_EXECUTOR} ../processor/main.py -l ${leftFilename} -r ${rightFilename} -s ${stitchedFilename} -o ${outputFilename}`
  return new Promise((resolve, reject) => {
    childProcess.exec(execCommand, { cwd: PYTHON_CWD }, (err, stdout) => {
      if (err) {
        reject(err)
      } else {
        console.log(stdout)
      }
    })
  })
}

async function createAndProcessSnapshot (): Promise<void> {
  // const timestamp = dayjs().format('YYYYMMDDHHmmss')
  // const [leftFilename, rightFilename] = await camera.snapshot(timestamp)
  // const stitchedFilename = timestamp + '__stitched.jpg'
  // const processedFilename = timestamp + '.jpg'
  await processSnapshot('parking_lot_left.jpg', 'parking_lot_right.jpg', 'parking_lot_stitched.jpg', 'parking_lot.jpg')
  // await processSnapshot(leftFilename, rightFilename, stitchedFilename, processedFilename)
}

export async function initLoop () {
  await createAndProcessSnapshot()
  setTimeout(async () => {
    initLoop()
  }, LOOP_TIMEOUT)
}
