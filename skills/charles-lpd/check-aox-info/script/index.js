#!/usr/bin/env node

const ENDPOINTS = {
  AOX: 'https://api.aox.xyz/info',
}

async function readInput() {
  return new Promise((resolve) => {
    let data = ''

    process.stdin.on('data', (chunk) => {
      data += chunk
    })

    process.stdin.on('end', () => {
      try {
        resolve(JSON.parse(data || '{}'))
      } catch {
        resolve({})
      }
    })
  })
}

async function fetchAOXInfo(url) {
  const res = await fetch(url)

  if (!res.ok) {
    throw new Error('not_found')
  }

  return res.json()
}

function output(data) {
  process.stdout.write(JSON.stringify(data))
}

async function main() {
  const input = await readInput()

  try {
    const aoxInfo = await fetchTx(`${ENDPOINTS.AOX}`)

    return output({
      success: true,
      data: aoxInfo
    })
  } catch (err) {
    if (err.message !== 'not_found') {
      return output({
        success: false,
        error: 'network_error'
      })
    }
  }
}

main()
