# Teapot Platform Scripts 🍵

All server management is now handled by a single unified script: `teapot.sh`

## Quick Commands

```bash
# Start everything
./teapot.sh start all

# Stop everything
./teapot.sh stop all

# Check status
./teapot.sh status

# Get help
./teapot.sh
```

## Full Command Structure

```bash
./teapot.sh [command] [target]
```

**Commands:** `start`, `stop`, `restart`, `status`

**Targets:** `all`, `backend`, `frontend`, `teapot-api`, `creator-api`

## Examples

| What you want to do | Command |
|---------------------|---------|
| Start all servers | `./teapot.sh start all` |
| Start only backend | `./teapot.sh start backend` |
| Start only frontend | `./teapot.sh start frontend` |
| Stop all servers | `./teapot.sh stop all` |
| Restart TeapotAPI | `./teapot.sh restart teapot-api` |
| Check what's running | `./teapot.sh status` |

## Features

✅ Single script to rule them all  
✅ Simple, intuitive commands  
✅ Port conflict detection  
✅ Status checking  
✅ Automatic logging to `logs/`  
✅ Graceful shutdown  
✅ Colorful terminal output  

## More Info

- **Quick Start**: See [QUICK-START.md](./QUICK-START.md)
- **Detailed Guide**: See [STARTUP-GUIDE.md](./STARTUP-GUIDE.md)

---

**That's it!** Just one script to start, stop, restart, and check your entire platform. 🚀
