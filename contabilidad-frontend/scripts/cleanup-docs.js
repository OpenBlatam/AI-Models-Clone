/**
 * Script para limpiar archivos de documentación duplicados
 * 
 * Este script mueve archivos de documentación duplicados a una carpeta de archivo
 * y mantiene solo los archivos esenciales en la raíz.
 */

const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, '..');
const archiveDir = path.join(rootDir, 'docs', 'archive');

// Archivos de documentación a archivar (mantener solo README.md y QUICK_START.md)
const docsToArchive = [
  'ABSOLUTE_FINAL_SUMMARY.md',
  'ADVANCED_IMPROVEMENTS.md',
  'COMPLETE_FEATURES_LIST.md',
  'COMPLETE_REFACTOR_DOCUMENTATION.md',
  'COMPLETE_REFACTOR_FINAL.md',
  'FEATURES_COMPLETE.md',
  'FINAL_COMPLETE_SUMMARY.md',
  'FINAL_REFACTOR_COMPLETE.md',
  'FINAL_REFACTOR_SUMMARY.md',
  'FINAL_SUMMARY.md',
  'IMPROVEMENTS.md',
  'PERFORMANCE_OPTIMIZATIONS.md',
  'README_REFACTOR.md',
  'REFACTOR_COMPLETE.md',
  'REFACTOR_FINAL_CLEAN.md',
  'REFACTORING_SUMMARY.md',
  'REFACTOR_SUMMARY.md',
  'ULTIMATE_COMPLETE_REFACTOR.md',
  'ULTIMATE_REFACTOR_SUMMARY.md',
  'UTILITIES_COMPLETE.md',
];

// Crear directorio de archivo si no existe
if (!fs.existsSync(archiveDir)) {
  fs.mkdirSync(archiveDir, { recursive: true });
}

// Mover archivos a archivo
docsToArchive.forEach(file => {
  const sourcePath = path.join(rootDir, file);
  const destPath = path.join(archiveDir, file);
  
  if (fs.existsSync(sourcePath)) {
    fs.renameSync(sourcePath, destPath);
    console.log(`✅ Archivado: ${file}`);
  }
});

console.log('\n✨ Limpieza de documentación completada!');
console.log(`📁 Archivos movidos a: ${archiveDir}`);
console.log('📄 Archivos mantenidos en raíz: README.md, QUICK_START.md');












