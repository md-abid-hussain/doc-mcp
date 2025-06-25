"""Kestra workflow management tab implementation."""

import logging
import os
from typing import  Optional, Tuple

import gradio as gr
import requests
from kestra import Flow

from ...database.repository import repository_manager

logger = logging.getLogger(__name__)


class KestraTab:
    """Handles the Kestra workflow management tab UI and logic."""

    def __init__(self, demo: Optional[gr.Blocks]):
        """Initialize the Kestra tab."""
        self.kestra_hostname = os.getenv("KESTRA_HOSTNAME", "http://localhost:8080")
        self.kestra_user = os.getenv("KESTRA_USER", "admin@localhost.dev")
        self.kestra_password = os.getenv("KESTRA_PASSWORD", "kestra")
        self.kestra_api_token = os.getenv("KESTRA_API_TOKEN", None)
        self.flow = Flow(wait_for_completion=False)
        self.flow.user = "admin@localhost.dev"
        self.flow.password = "kestra"
        self.demo = demo

    def create_tab(self) -> gr.TabItem:
        """Create the Kestra workflow management tab interface."""
        with gr.TabItem("⚙️ Kestra Workflows", visible=True) as tab:
            gr.Markdown("### 🔄 Kestra Workflow Management")
            gr.Markdown("Simple interface to check Kestra server status and trigger workflows.")

            # Server status section
            with gr.Row():
                with gr.Column(scale=2):
                    with gr.Row():
                        check_status_btn = gr.Button(
                            "🔍 Check Server Status", 
                            variant="secondary",
                            size="sm"
                        )
                        
                    server_status = gr.Textbox(
                        label="Kestra Server Status",
                        value="Click 'Check Server Status' to verify connection...",
                        interactive=False,
                        lines=3
                    )

                with gr.Column(scale=1):
                    hostname_input = gr.Textbox(
                        label="Kestra Hostname",
                        value=self.kestra_hostname,
                        placeholder="http://localhost:8080"
                    )

            # Workflow execution section
            gr.Markdown("### 🚀 Workflow Execution")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("#### Batch Processing")
                    batch_controller_btn = gr.Button(
                        "🔄 Run Repo Ingestion Controller",
                        variant="primary",
                        size="lg"
                    )
                    
                with gr.Column(scale=1):
                    gr.Markdown("#### Single Repository")
                    with gr.Row():
                        repo_dropdown = gr.Dropdown(
                            label="Select Repository from Database",
                            choices=[],
                            interactive=True
                        )
                        refresh_repos_btn = gr.Button(
                            "🔄",
                            size="sm",
                            variant="secondary"
                        )
                    
                    single_repo_btn = gr.Button(
                        "📦 Ingest Selected Repository",
                        variant="primary",
                        size="lg",
                        interactive=False
                    )

            # Execution results
            with gr.Row():
                with gr.Column(scale=1):
                    execution_status = gr.Textbox(
                        label="Execution Status",
                        value="No workflow executed yet...",
                        interactive=False,
                        lines=6
                    )

                with gr.Column(scale=1):
                    execution_logs = gr.Textbox(
                        label="Execution Logs",
                        value="Logs will appear here after execution...",
                        interactive=False,
                        lines=6
                    )

            # Event handlers
            check_status_btn.click(
                fn=self._check_server_status,
                inputs=[hostname_input],
                outputs=[server_status],
                show_api=False
            )

            refresh_repos_btn.click(
                fn=self._load_repositories,
                outputs=[repo_dropdown],
                show_api=False
            )

            repo_dropdown.change(
                fn=lambda repo: gr.Button(interactive=bool(repo)),
                inputs=[repo_dropdown],
                outputs=[single_repo_btn],
                show_api=False
            )

            batch_controller_btn.click(
                fn=self._execute_batch_controller,
                inputs=[hostname_input],
                outputs=[execution_status, execution_logs],
                show_api=False
            )

            single_repo_btn.click(
                fn=self._execute_single_repo,
                inputs=[repo_dropdown, hostname_input],
                outputs=[execution_status, execution_logs],
                show_api=False
            )

            # Load repositories on tab creation
            self.demo.load(
                fn=self._load_repositories,
                outputs=[repo_dropdown],
                show_api=False
            )

        return tab

    def _check_server_status(self, hostname: str) -> str:
        """Check if Kestra server is running and accessible."""
        try:
            self.kestra_hostname = hostname or self.kestra_hostname

            # Try to connect to Kestra API
            auth = None
            if self.kestra_user and self.kestra_password:
                auth = (self.kestra_user, self.kestra_password)

            headers = {}
            if self.kestra_api_token:
                headers["Authorization"] = f"Bearer {self.kestra_api_token}"

            response = requests.get(
                f"{self.kestra_hostname}/api/v1/flows/company.team",
                auth=auth,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                
                status_msg = "✅ **Server Connected**\n"
                status_msg += f"🌐 Host: {self.kestra_hostname}\n"
                status_msg += f"⏰ Response: {response.elapsed.total_seconds():.2f}s"

                logger.info(f"Kestra server connection successful: {self.kestra_hostname}")
                return status_msg
            else:
                error_msg = "❌ **Connection Error**\n"
                error_msg += f"🌐 Host: {self.kestra_hostname}\n"
                error_msg += f"📟 Status: {response.status_code}"
                return error_msg

        except requests.exceptions.ConnectionError:
            error_msg = "❌ **Connection Failed**\n"
            error_msg += f"🌐 Host: {self.kestra_hostname}\n"
            error_msg += "💡 Check if Kestra is running"
            return error_msg

        except Exception as e:
            error_msg = "❌ **Unknown Error**\n"
            error_msg += f"📝 Error: {str(e)}"
            return error_msg

    def _load_repositories(self) -> gr.Dropdown:
        """Load repositories from the database."""
        try:
            # Use the repository_manager to get available repositories
            repo_choices = repository_manager.get_available_repositories()
            
            logger.info(f"Loaded {len(repo_choices)} repositories from database")
            return gr.Dropdown(choices=repo_choices, value=None)
            
        except Exception as e:
            logger.error(f"Failed to load repositories: {e}")
            return gr.Dropdown(choices=[], value=None)

    def _execute_batch_controller(self, hostname: str) -> Tuple[str, str]:
        """Execute the repo-ingestion-controller workflow."""
        try:
            # Update environment variables for Kestra client
            os.environ["KESTRA_HOSTNAME"] = hostname or self.kestra_hostname
            if self.kestra_user:
                os.environ["KESTRA_USER"] = self.kestra_user
            if self.kestra_password:
                os.environ["KESTRA_PASSWORD"] = self.kestra_password

            # Create Flow instance and execute (no inputs needed)
            
            logger.info("Executing Kestra batch controller workflow")
            
            result = self.flow.execute(
                namespace="company.team",
                flow="repo-ingestion-controller",
                inputs={}  # No inputs required
            )

            # Format execution status
            status_msg = "🚀 **Batch Controller Executed**\n\n"
            status_msg += f"🆔 **Execution ID:** {getattr(result, 'execution_id', 'N/A')}\n"
            status_msg += f"📊 **Status:** {getattr(result, 'status', 'N/A')}\n"
            status_msg += "📋 **Workflow:** repo-ingestion-controller"

            # Format logs
            logs_text = getattr(result, 'log', 'No logs available.')
            if hasattr(result, 'error') and result.error:
                logs_text += f"\n\n❌ **Error:** {result.error}"

            logger.info("Batch controller workflow execution completed")
            return status_msg, logs_text

        except Exception as e:
            error_msg = "❌ **Batch Controller Failed**\n\n"
            error_msg += f"📝 **Error:** {str(e)}"

            logger.error(f"Batch controller workflow execution failed: {str(e)}")
            return error_msg, f"Execution failed: {str(e)}"

    def _execute_single_repo(self, repo_name: str, hostname: str) -> Tuple[str, str]:
        """Execute the single-repo-ingestion workflow."""
        if not repo_name:
            return "❌ Please select a repository.", "No logs available."

        try:
            # Update environment variables for Kestra client
            os.environ["KESTRA_HOSTNAME"] = hostname or self.kestra_hostname
            if self.kestra_user:
                os.environ["KESTRA_USER"] = self.kestra_user
            if self.kestra_password:
                os.environ["KESTRA_PASSWORD"] = self.kestra_password
                
            # Prepare inputs
            inputs = {
                "repo_name": repo_name,
                "branch": "main"
            }

            
            logger.info(f"Executing single repo workflow for: {repo_name}")
            
            result = self.flow.execute(
                namespace="company.team",
                flow="single-repo-ingestion",
                inputs=inputs
            )

            # Format execution status
            status_msg = "🚀 **Single Repo Ingestion Executed**\n\n"
            status_msg += f"📦 **Repository:** {repo_name}\n"
            status_msg += f"🆔 **Execution ID:** {getattr(result, 'execution_id', 'N/A')}\n"
            status_msg += f"📊 **Status:** {getattr(result, 'status', 'N/A')}\n"
            status_msg += "🌿 **Branch:** main"

            # Format logs
            logs_text = getattr(result, 'log', 'No logs available.')
            if hasattr(result, 'error') and result.error:
                logs_text += f"\n\n❌ **Error:** {result.error}"

            logger.info(f"Single repo workflow execution completed: {repo_name}")
            return status_msg, logs_text

        except Exception as e:
            error_msg = "❌ **Single Repo Ingestion Failed**\n\n"
            error_msg += f"📦 **Repository:** {repo_name}\n"
            error_msg += f"📝 **Error:** {str(e)}"

            logger.error(f"Single repo workflow execution failed: {repo_name} - {str(e)}")
            return error_msg, f"Execution failed: {str(e)}"