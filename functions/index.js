const functions = require('firebase-functions');
const admin = require('firebase-admin');

admin.initializeApp();
const db = admin.firestore();

// Scheduled function: prune device logs older than LOG_RETENTION_DAYS (default 30)
exports.pruneOldLogs = functions.pubsub.schedule('every 24 hours').onRun(async (context) => {
  const days = process.env.LOG_RETENTION_DAYS ? parseInt(process.env.LOG_RETENTION_DAYS) : 30;
  const cutoff = Date.now() - (days * 24 * 60 * 60 * 1000);

  // Iterate devices and remove old logs in batches
  const devicesSnap = await db.collection('devices').get();
  const deletes = [];

  for (const deviceDoc of devicesSnap.docs) {
    const logsRef = deviceDoc.ref.collection('logs');
    // Query logs older than cutoff; assumes logs store a `timestamp` field as Firestore Timestamp
    const oldLogsQuery = logsRef.where('timestamp', '<', new Date(cutoff)).limit(500);
    const oldLogsSnap = await oldLogsQuery.get();
    if (oldLogsSnap.empty) continue;

    const batch = db.batch();
    oldLogsSnap.docs.forEach(d => batch.delete(d.ref));
    deletes.push(batch.commit());
  }

  await Promise.all(deletes);
  return null;
});

// HTTP trigger for ad-hoc pruning (protected by callable auth in prod)
exports.pruneOldLogsHttp = functions.https.onRequest(async (req, res) => {
  // In production, verify admin privileges via ID token or other mechanism
  try {
    await exports.pruneOldLogs();
    res.status(200).send('Prune triggered');
  } catch (err) {
    console.error(err);
    res.status(500).send('Error pruning logs');
  }
});
