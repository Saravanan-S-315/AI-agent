# Production Deployment Checklist

## Pre-Deployment

- [ ] All tests passing: `pytest -v --cov=app --cov-fail-under=80`
- [ ] No linting issues: `flake8 app tests`
- [ ] Type checking clean: `mypy app --ignore-missing-imports`
- [ ] Security scan passed: Review security vulnerabilities
- [ ] Code reviewed: At least 2 approvals
- [ ] Changelog updated: Document all changes
- [ ] Documentation updated: README, PRODUCTION_GUIDE.md
- [ ] Performance tested: Load tested if applicable
- [ ] Database backup strategy confirmed
- [ ] Rollback plan documented

## Infrastructure Setup

### Database
- [ ] SQLite database location identified
- [ ] Backup directory created and accessible
- [ ] Backup retention policy configured (default: 10 backups)
- [ ] Database integrity verified: `make health-check`
- [ ] WAL mode enabled for better concurrency

### Logging
- [ ] Logs directory writable and accessible
- [ ] Log rotation configured (10MB, 5 backups)
- [ ] Log aggregation tool configured (ELK, Splunk, etc.)
- [ ] Alerting rules set for ERROR/CRITICAL levels
- [ ] Log cleanup policy defined (retention period)

### Monitoring
- [ ] Health check endpoint configured
- [ ] Metrics collection enabled (if applicable)
- [ ] Alerting thresholds set:
  - [ ] High memory usage (>80%)
  - [ ] Disk space low (<100MB)
  - [ ] Lock acquisition failures
  - [ ] Validation failure rate > 50%

### Git Integration (if using auto-git)
- [ ] GitHub token generated and stored securely
- [ ] Repository target verified
- [ ] Branch naming convention configured
- [ ] PR template created
- [ ] Branch protection rules set

## Container Deployment (Docker)

- [ ] Base image security verified
- [ ] Dockerfile vulnerability scan clean
- [ ] Container registry credentials configured
- [ ] Image tags strategy defined (latest, version, date)
- [ ] Container health check endpoint working
- [ ] Volume mounts tested and working
- [ ] Environment variables externalized

### Kubernetes (if applicable)
- [ ] CronJob schedule verified
- [ ] PersistentVolume configured and tested
- [ ] Resource limits set (CPU, memory)
- [ ] ServiceAccount created with minimal permissions
- [ ] RBAC policies configured
- [ ] Network policies configured

## CI/CD Pipeline

- [ ] GitHub Actions workflow verified
- [ ] All tests run in CI environment
- [ ] Docker image builds and pushes successfully
- [ ] Security scanning integrated and passing
- [ ] Code coverage reports generated
- [ ] Artifacts stored securely
- [ ] Failed job notifications configured

## Security

- [ ] Input validation reviewed
- [ ] Dependency audit passed: `pip install -U pip-audit && pip-audit`
- [ ] Secrets management configured (no hardcoded credentials)
- [ ] Database encryption enabled (if needed)
- [ ] Access control reviewed (file permissions, ownership)
- [ ] Security scanning rules reviewed
- [ ] Audit logging enabled
- [ ] Network security groups configured

## Performance & Scalability

- [ ] Database query optimization reviewed
- [ ] Index strategy confirmed
- [ ] Lock timeout values appropriate for workload
- [ ] Concurrent execution strategy verified
- [ ] Resource limits tested under load
- [ ] Backup/restore performance acceptable
- [ ] Log rotation doesn't impact performance

## Backup & Disaster Recovery

- [ ] Backup creation tested: `make backup`
- [ ] Restore procedure tested: `make restore`
- [ ] Backup storage location secure
- [ ] Backup encryption enabled
- [ ] RTO (Recovery Time Objective) and RPO (Recovery Point Objective) defined
- [ ] Disaster recovery runbook created
- [ ] Team trained on recovery procedures

## Compliance & Audit

- [ ] Data retention policy defined
- [ ] Data deletion/archival process implemented
- [ ] Audit logs configured and accessible
- [ ] Compliance requirements identified and met
- [ ] Privacy policy reviewed (if handling user data)
- [ ] Terms of service updated

## Documentation

- [ ] Installation guide updated
- [ ] Configuration guide completed: `.env.example` reviewed
- [ ] Troubleshooting guide created
- [ ] Runbook for common operations written
- [ ] Architecture diagram created
- [ ] API documentation generated (if applicable)
- [ ] Known issues and limitations documented

## Monitoring & Alerting

```python
# Health check command for monitoring
from app.health import HealthChecker
from app.config import AgentConfig

config = AgentConfig()
checker = HealthChecker(config.memory_db_path, config.workspace_root)
health = checker.check()
# Alert if health.status != "healthy"
```

## Deployment Commands

```bash
# 1. Pull latest code
git pull origin main

# 2. Run pre-deployment checks
python -c "
import subprocess
checks = [
    ('Tests', 'pytest -q'),
    ('Linting', 'flake8 app tests --count'),
    ('Type checking', 'mypy app --ignore-missing-imports'),
]
for name, cmd in checks:
    result = subprocess.run(cmd.split(), capture_output=True)
    status = 'PASS' if result.returncode == 0 else 'FAIL'
    print(f'{name}: {status}')
"

# 3. Create backup
make backup

# 4. Deploy (choose your deployment method)

# Local
python main.py

# Docker
docker-compose up -d

# Kubernetes
kubectl apply -f deployment.yaml

# 5. Monitor deployment
make health-check
tail -f logs/autodev.log

# 6. Verify functionality
# Check generated_projects/ for new projects
# Check logs/ for success messages
```

## Post-Deployment

- [ ] System health check passed: `make health-check`
- [ ] Applications logs clean (no errors)
- [ ] Monitoring dashboard showing healthy metrics
- [ ] Database accessible and responsive
- [ ] Backup system working
- [ ] All smoke tests passing
- [ ] Team notified of deployment
- [ ] Change log updated with deployment timestamp

## Rollback Plan

If deployment fails:

1. [ ] Stop current deployment
2. [ ] Check error logs: `tail -f logs/errors.log`
3. [ ] Restore from backup if database corrupted: `make restore`
4. [ ] Revert code: `git revert <commit>`
5. [ ] Redeploy previous version
6. [ ] Post-incident review

## Maintenance Schedule

- **Daily**: Monitor logs and health checks
- **Weekly**: Review performance metrics and disk usage
- **Monthly**: Test backup/restore procedure
- **Quarterly**: Security audit and dependency updates
- **Annually**: Full disaster recovery test

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Approved By**: _______________

