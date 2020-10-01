pipeline {
    agent any

    environment {
        STAGING_KAPACITOR_URL = 'http://localhost:9092'
        STAGING_KAPACITOR_DB = 'staging_performance'
        STAGING_KAPACITOR_SLACK_CHANNEL = '#app-staging-alerts'
        STAGING_ASE_URL = 'https://staging-ase-internal.outcomehealthtech.com:443'
        STAGING_LS_URL = 'https://staging-ls-internal.outcomehealthtech.com:443'
        STAGING_MDM_URL = 'https://mdm-staging-org-internal.outcomehealthtech.com:443'

        PRODUCTION_KAPACITOR_URL = 'http://localhost-prod:9092'
        PRODUCTION_KAPACITOR_DB = 'production_performance'
        PRODUCTION_KAPACITOR_SLACK_CHANNEL = '#app-production-alerts'
        PRODUCTION_ASE_URL = 'https://ase-internal.outcomehealthtech.com:443'
        PRODUCTION_LS_URL = 'https://ls-internal.outcomehealthtech.com:443'
        PRODUCTION_MDM_URL = 'https://mdm-org-internal.outcomehealthtech.com:443'
    }

    stages {

        // Sets variables defined by the branch name
        stage('Get/Set Environment') {
            steps {
                script {
                    env.DEPLOY = "1"

                    def envMap = [:]
                    // production only tagged commits, not ending in -rc
                    if (env.TAG_NAME && env.TAG_NAME ==~ /^\d+\.\d+\.\d+$/) {
                        envMap = [ohEnv           : 'production',
                                  kapacitorUrl    : "${PRODUCTION_KAPACITOR_URL}",
                                  kapacitorDb     : "${PRODUCTION_KAPACITOR_DB}",
                                  slackChannel    : "${PRODUCTION_KAPACITOR_SLACK_CHANNEL}",
                                  aseUrl          : "${PRODUCTION_ASE_URL}",
                                  lsUrl           : "${PRODUCTION_LS_URL}",
                                  mdmUrl          : "${PRODUCTION_MDM_URL}"
                                 ]
                        echo 'PROD TAG'
                    }
                    // staging has tagged commits with -rc in the end
                    else if ((env.TAG_NAME && env.TAG_NAME ==~ /^\d+\.\d+\.\d+-rc.*$/) ||
                            env.BRANCH_NAME ==~ /^(release|hotfix)-.*/) {
                        envMap = [ohEnv           : 'staging',
                                  kapacitorUrl    : "${STAGING_KAPACITOR_URL}",
                                  kapacitorDb     : "${STAGING_KAPACITOR_DB}",
                                  slackChannel    : "${STAGING_KAPACITOR_SLACK_CHANNEL}",
                                  aseUrl          : "${STAGING_ASE_URL}",
                                  lsUrl           : "${STAGING_LS_URL}",
                                  mdmUrl          : "${STAGING_MDM_URL}"
                                 ]
                        echo 'STAGING TAG'
                    }
                    // other branches can compile and test, but no image will be created
                    else {
                        envMap = [ohEnv           : 'test']
                        echo 'BRANCH'
                        env.DEPLOY = "0"
                    }

                    env.ohEnv = envMap.ohEnv
                    env.kapacitorUrl = envMap.kapacitorUrl
                    env.kapacitorDb = envMap.kapacitorDb
                    env.slackChannel = envMap.slackChannel
                    env.aseUrl = envMap.aseUrl
                    env.lsUrl = envMap.lsUrl
                    env.mdmUrl = envMap.mdmUrl
                }
            }
        }

        stage("deploy") {
            when {
                not {
                    environment name: 'ohEnv', value: 'test'
                }
            }
            steps {
                echo 'Deploying the scripts...'
                echo "kapacitor URL: ${env.kapacitorUrl}"
                echo "kapacitor DB: ${env.kapacitorDb}"
                echo "slackChannel: ${env.slackChannel}"
                echo "aseUrl: ${env.aseUrl}"
                echo "lsUrl: ${env.lsUrl}"
                echo "mdmUrl: ${env.mdmUrl}"

                withCredentials([
                    usernamePassword(credentials: 'credentials-kapacitor', usernameVariable: KAPACITOR_USER, passwordVariable: KAPACITOR_PASSWORD)
                ]) {
                    echo "user: ${KAPACITOR_USER}"
                    echo "pwd: ${KAPACITOR_PASSWORD}"
                }
            }
        }
    }
}