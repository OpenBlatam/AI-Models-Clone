/**
 * Unit Tests - Backup Manager
 */

import { BackupManager, getBackupManager } from '@/lib/backup-manager'

describe('BackupManager', () => {
  let backupManager: BackupManager

  beforeEach(() => {
    backupManager = new BackupManager()
    if (typeof window !== 'undefined') {
      localStorage.clear()
    }
  })

  afterEach(() => {
    backupManager.clear()
  })

  describe('Backup Creation', () => {
    it('should create backup', () => {
      const data = {
        models: [{ id: '1', name: 'test' }],
        queue: [{ id: '2', name: 'test2' }],
      }

      const backup = backupManager.createBackup(data)
      expect(backup).toBeDefined()
      expect(backup.timestamp).toBeDefined()
      expect(backup.data).toEqual(data)
    })

    it('should store backup in localStorage', () => {
      const data = { models: [], queue: [] }
      backupManager.createBackup(data)

      // Backup should be stored
      const backups = backupManager.getAllBackups()
      expect(backups.length).toBeGreaterThan(0)
    })

    it('should limit number of backups', () => {
      // Create many backups
      for (let i = 0; i < 150; i++) {
        backupManager.createBackup({ models: [], queue: [] })
      }

      const backups = backupManager.getAllBackups()
      expect(backups.length).toBeLessThanOrEqual(100)
    })
  })

  describe('Backup Restoration', () => {
    it('should restore from backup', () => {
      const data = {
        models: [{ id: '1', name: 'test' }],
        queue: [{ id: '2', name: 'test2' }],
      }

      const backup = backupManager.createBackup(data)
      const restored = backupManager.restoreBackup(backup.id)

      expect(restored).toEqual(data)
    })

    it('should handle invalid backup ID', () => {
      const restored = backupManager.restoreBackup('invalid-id')
      expect(restored).toBeNull()
    })
  })

  describe('Auto Backup', () => {
    it('should start auto backup', (done) => {
      const stop = backupManager.startAutoBackup(
        { models: [], queue: [] },
        100 // 100ms interval
      )

      setTimeout(() => {
        const backups = backupManager.getAllBackups()
        expect(backups.length).toBeGreaterThan(0)
        stop()
        done()
      }, 200)
    })

    it('should stop auto backup', (done) => {
      const stop = backupManager.startAutoBackup(
        { models: [], queue: [] },
        100
      )

      stop()

      setTimeout(() => {
        const initialCount = backupManager.getAllBackups().length
        setTimeout(() => {
          const finalCount = backupManager.getAllBackups().length
          expect(finalCount).toBe(initialCount)
          done()
        }, 200)
      }, 50)
    })
  })

  describe('Backup Management', () => {
    it('should get all backups', () => {
      backupManager.createBackup({ models: [], queue: [] })
      backupManager.createBackup({ models: [], queue: [] })

      const backups = backupManager.getAllBackups()
      expect(backups.length).toBe(2)
    })

    it('should get latest backup', async () => {
      backupManager.createBackup({ models: [], queue: [] })
      await new Promise(resolve => setTimeout(resolve, 10))
      const latest = backupManager.createBackup({ models: [], queue: [] })

      const retrievedLatest = backupManager.getLatestBackup()
      expect(retrievedLatest?.id).toBe(latest.id)
    })

    it('should delete backup', () => {
      const backup = backupManager.createBackup({ models: [], queue: [] })
      backupManager.deleteBackup(backup.id)

      const backups = backupManager.getAllBackups()
      expect(backups.find(b => b.id === backup.id)).toBeUndefined()
    })

    it('should clear all backups', () => {
      backupManager.createBackup({ models: [], queue: [] })
      backupManager.createBackup({ models: [], queue: [] })

      backupManager.clear()
      const backups = backupManager.getAllBackups()
      expect(backups.length).toBe(0)
    })
  })

  describe('Backup Export/Import', () => {
    it('should export backup', () => {
      const backup = backupManager.createBackup({
        models: [{ id: '1', name: 'test' }],
        queue: [],
      })

      const exported = backupManager.exportBackup(backup.id)
      expect(exported).toBeDefined()
      expect(exported).toContain('models')
    })

    it('should import backup', () => {
      const backup = backupManager.createBackup({
        models: [{ id: '1', name: 'test' }],
        queue: [],
      })

      const exported = backupManager.exportBackup(backup.id)
      const imported = backupManager.importBackup(exported)

      expect(imported).toBeDefined()
      expect(imported?.data.models).toHaveLength(1)
    })
  })

  describe('Singleton', () => {
    it('should return same instance', () => {
      const b1 = getBackupManager()
      const b2 = getBackupManager()
      expect(b1).toBe(b2)
    })
  })
})


