from doc_sync_bot.llm_generator.client import LLMClient

def process_pr_refinements(gh_client, 
                            repo_name: str, 
                            pr_number: int, 
                            file_path: str, 
                            branch_name: str, 
                            llm_client: LLMClient) -> list:
    """
    Scans PR comments for feedback prefixed with `@docs-bot`.
    Refines documentation based on feedback and commits updates directly back to the PR.
    """
    if not gh_client.g:
        print("GitHub Client is not authenticated. Skipping live refinements.")
        return []
        
    repo = gh_client.g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    # Issue comments in PyGithub contain PR comments
    comments = list(pr.get_issue_comments())
    
    # Filter comments posted by the bot (identifiable by the signature tag)
    bot_signature = "docs-sync-bot"
    bot_comments = [c.body for c in comments if bot_signature in c.body]
    
    processed_comments = []
    
    for comment in comments:
        body = comment.body.strip()
        if body.startswith("@docs-bot"):
            comment_marker = f"<!-- Refined comment ID: {comment.id} -->"
            
            # Verify if this comment was already processed by searching bot comments for this marker
            already_replied = any(comment_marker in bot_body for bot_body in bot_comments)
            if already_replied:
                continue
                
            feedback = body.replace("@docs-bot", "").strip()
            print(f"Found new docs refinement request: '{feedback}' (Comment ID: {comment.id})")
            
            # Fetch current state of file on the sync branch
            try:
                file_contents = repo.get_contents(file_path, ref=branch_name)
                current_doc = file_contents.decoded_content.decode('utf-8')
            except Exception as e:
                print(f"Could not load '{file_path}' from branch '{branch_name}': {e}. Skipping refinement.")
                continue
                
            # Ask the LLM to refine the document based on the feedback
            print("Refining documentation with feedback...")
            refined_doc = llm_client.refine_documentation(current_doc, feedback)
            
            # Commit the refined content back to the PR branch
            commit_msg = f"docs: Refined based on PR comment review #{comment.id}"
            try:
                repo.update_file(
                    path=file_path,
                    message=commit_msg,
                    content=refined_doc,
                    sha=file_contents.sha,
                    branch=branch_name
                )
                print(f"Committed refined documentation to branch '{branch_name}'.")
            except Exception as e:
                print(f"Failed to update file on branch: {e}")
                continue
                
            # Reply to the user's comment to close the loop
            reply_body = (
                f"### Documentation Refinement Successful!\n\n"
                f"I've updated the documentation based on your feedback: *\"{feedback}\"*\n"
                f"The changes have been pushed directly to your PR branch.\n\n"
                f"<!-- {bot_signature} -->\n"
                f"{comment_marker}"
            )
            pr.create_issue_comment(reply_body)
            print("Posted comment reply to PR.")
            processed_comments.append((comment.id, feedback))
            
    return processed_comments
