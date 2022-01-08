import * as jfs from 'jfs'
import * as path from 'path'

const DATA_FILE = path.join(__dirname, '../data/history.json')
const store = new jfs(DATA_FILE, { saveId: 'timestamp' })
