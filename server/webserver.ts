import * as express from 'express'
import * as path from 'path'
import * as cors from 'cors'
import * as dotenv from 'dotenv'

dotenv.config({
  path: path.join(__dirname, '../.env')
})

const app = express()

app.set('view engine', 'ejs')
app.set('views', path.join(__dirname, '../client'))

app.use(cors())
app.use('/img', express.static(path.join(__dirname, '../data/processed')))

app.get('/', (req, res) => {
  res.render('index')
})

export function listen (): Promise<void> {
  return new Promise(resolve => {
    const server = app.listen(process.env.HTTP_PORT, () => {
      const address = server.address()
      const port = (typeof address === 'object') ? address.port : address
      console.log(`HTTP-Server listening on port ${port}`)
    })
  })
}
