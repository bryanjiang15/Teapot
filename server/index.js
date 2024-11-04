import Fastify from 'fastify'
import sqlite3 from 'sqlite3'
import cors from '@fastify/cors'

const fastify = Fastify({
  logger: true,
  requestTimeout: 60 * 1000
})

// Declare a route
fastify.get('/', async function handler (request, reply) {
  return { hello: 'world' }
})

await fastify.register(cors, {
    // put your options here
})

const db = new sqlite3.Database("cache.db");

// Run the server!
try {
  await fastify.listen({ port: 3000 })
} catch (err) {
  fastify.log.error(err)
  process.exit(1)
}