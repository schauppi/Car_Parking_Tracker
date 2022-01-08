import * as dotenv from 'dotenv'
import * as childProcess from 'child_process'
import * as path from 'path'
import * as dayjs from 'dayjs'
import * as camera from './camera'

dotenv.config({
  path: path.join(__dirname, '../.env')
})

const LOOP_TIMEOUT = parseInt(process.env.LOOP_TIMEOUT || '5000')
const PYTHON_EXECUTOR = process.env.PYTHON_PATH || 'py'

function processSnapshot (leftFilename: string, rightFilename: string): Promise<any> {
  console.log(process.cwd())
  const execCommand = `${PYTHON_EXECUTOR} ../processor/main.py -l ${leftFilename} -r ${rightFilename}`
  return new Promise((resolve, reject) => {
    childProcess.exec(execCommand, (err, stdout) => {
      if (err) {
        reject(err)
      } else {
        console.log(stdout)
      }
    })
  })
}

async function createAndProcessSnapshot () {
  const timestamp = dayjs().format('YYYYMMDDHHmmss')
  const [leftFilename, rightFilename] = await camera.snapshot(timestamp)
  await processSnapshot(leftFilename, rightFilename)
}

export async function initLoop () {
  await createAndProcessSnapshot()
  setTimeout(async () => {
    initLoop()
  }, LOOP_TIMEOUT)
}
