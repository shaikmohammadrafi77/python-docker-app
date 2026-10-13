
pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'git@github.com:shaikmohammadrafi77/e-bugtracker.git'
            }
        }

        stage('Check Python') {
            steps {
                sh 'python3 --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                dir('Project') {
                    sh 'python3 -m venv .venv'
                    sh '.venv/bin/pip install -r requirements.txt'
                }
            }
        }

        stage('Validate Application') {
            steps {
                dir('Project') {
                    sh '.venv/bin/python -m py_compile app.py'
                }
            }
        }

        stage('Run Automated Tests') {
            steps {
                dir('Project') {
                    sh '.venv/bin/python -m pip install unittest-xml-reporting'
                    sh '.venv/bin/python -m xmlrunner discover -s . -p "test_app.py" -o test-reports'
                }
            }

            post {
                always {
                    junit 'Project/test-reports/*.xml'
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'bugtracker-ec2-ssh',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    sh '''
                        set -eu

                        echo "Creating release archive..."

                        tar -czf bugtracker-release.tar.gz \
                            -C Project app.py requirements.txt templates

                        echo "Copying release to application EC2..."

                        scp -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=accept-new \
                            bugtracker-release.tar.gz \
                            "$SSH_USER@10.0.1.13:/tmp/bugtracker-release.tar.gz"

                        echo "Deploying application..."

                        ssh -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=accept-new \
                            "$SSH_USER@10.0.1.13" 'set -eu

                                APP_DIR=/home/ec2-user/e-bugtracker/Project
                                RELEASE_DIR=$(mktemp -d /tmp/bugtracker-release.XXXXXX)

                                cleanup() {
                                    rm -rf "$RELEASE_DIR"
                                    rm -f /tmp/bugtracker-release.tar.gz
                                }
                                trap cleanup EXIT

                                tar -xzf /tmp/bugtracker-release.tar.gz \
                                    -C "$RELEASE_DIR"

                                cp "$RELEASE_DIR/app.py" \
                                    "$APP_DIR/app.py"

                                cp "$RELEASE_DIR/requirements.txt" \
                                    "$APP_DIR/requirements.txt"

                                cp -a "$RELEASE_DIR/templates/." \
                                    "$APP_DIR/templates/"

                                "$APP_DIR/.venv/bin/pip" install \
                                    -r "$APP_DIR/requirements.txt"

                                echo "Restarting bugtracker service..."

                                sudo systemctl restart bugtracker

                                sudo systemctl is-active --quiet bugtracker

                                echo "Waiting for application health check..."

                                for i in $(seq 1 12); do
                                    if curl -fsS \
                                        http://127.0.0.1:5000/ \
                                        >/dev/null; then

                                        echo "Application health check passed"
                                        break
                                    fi

                                    if [ "$i" -eq 12 ]; then
                                        echo "Application health check failed"

                                        sudo journalctl \
                                            -u bugtracker \
                                            -n 50 \
                                            --no-pager

                                        exit 1
                                    fi

                                    sleep 5
                                done

                                echo "Deployment successful"
                            '
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check Console Output for details.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}
