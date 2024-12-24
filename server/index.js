import Fastify from 'fastify'
import sqlite3 from 'sqlite3'
import cors from '@fastify/cors'
import {db, initializeDatabase} from './database.js'
import {craft_new_word, capitalizeFirstLetter, craft_new_card} from './craft_card.js'

const fastify = Fastify({
  logger: true,
  requestTimeout: 60 * 1000
})

// Declare a route
// fastify.get('/', async function handler (request, reply) {
//   return { hello: 'world' }
// })

await fastify.register(cors, {
    // put your options here
    origin: 'http://localhost:3000', // Allow requests from the React app
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    credentials: true
})

//const db = new sqlite3.Database("cache.db");
initializeDatabase();

fastify.route({
  method: 'GET',
  url: '/',
  schema: {
      // the response needs to be an object with an `hello` property of type 'string'
      response: {
          200: {
              type: 'object',
              properties: {
                  hello: { type: 'string'}
              }
          }
      },
  },
  // this function is executed for every request before the handler is executed
  preHandler: async (request, reply) => {
      // E.g. check authentication
  },
  handler: async (request, reply) => {
      reply.type('application/json').code(200)

      return {
      }
  }
})

fastify.route({
    method: 'POST',
    url: '/',
    schema: {
      response: {
        200: {
          type: 'object',
          properties: {
            result: { type: 'string' },
            emoji: { type: 'string' }
          }
        }
      }
    },
    preHandler: async (request, reply) => {
      // E.g. check authentication
    },
    handler: async (request, reply) => {

        if (!request?.body?.first || !request?.body?.second) {
            return;
        }

        const firstWord = capitalizeFirstLetter(request.body.first.trim().toLowerCase());
        const secondWord = capitalizeFirstLetter(request.body.second.trim().toLowerCase());
        reply.type('application/json').code(200)

        return await craft_new_word(firstWord, secondWord)
    }
})

fastify.route({
    method: 'POST',
    url: '/new-card',
    schema: {
      response: {
        200: {
          type: 'object',
          properties: {
            name: { type: 'string' },
            rarity: { type: 'string' },
            power: { type: 'number' },
            emoji: { type: 'string' },
            health: { type: 'number' },
          }
        }
      }
    },
    preHandler: async (request, reply) => {
      // E.g. check authentication
    },
    handler: async (request, reply) => {
      if (!request?.body?.word) {
        return;
      }

      const word = capitalizeFirstLetter(request.body.word.trim().toLowerCase());
      reply.type('application/json').code(200)

      return await craft_new_card(word)
    }
})

// Run the server!
try {
  await fastify.listen({ port: 3001, host: '0.0.0.0'})
} catch (err) {
  fastify.log.error(err)
  process.exit(1)
}