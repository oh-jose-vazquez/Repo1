pipeline {
    agent any

    stages {

        // Sets variables defined by the branch name
        stage('Get/Set Environment') {
            steps {
                script {
                    env.DEPLOY = "1"

                    def envMap = [:]
                    // production only tagged commits, not ending in -rc
                    if (env.TAG_NAME && env.TAG_NAME ==~ /^\d+\.\d+\.\d+$/) {
                        envMap = [ohEnv           : 'production']
                        echo 'PROD TAG'
                    }
                    // staging has tagged commits with -rc in the end
                    else if ((env.TAG_NAME && env.TAG_NAME ==~ /^\d+\.\d+\.\d+-rc.*$/) ||
                            env.BRANCH_NAME ==~ /^(release|hotfix)-.*/) {
                        envMap = [ohEnv           : 'staging']
                        echo 'STAGING TAG'
                    }
                    // other branches can compile and test, but no image will be created
                    else {
                        envMap = [ohEnv           : 'test']
                        echo 'BRANCH'
                        env.DEPLOY = "0"
                    }

                    env.ohEnv = envMap.ohEnv
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
            }
        }
    }
}