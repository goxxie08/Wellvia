from datetime import date
from app.models.db import execute_query
from app.services.gamification import add_user_points, check_and_award_achievements, POINTS_MAP

def get_user_journal_entries(user_id):
    """Retrieve all gratitude journal entries for authenticated student."""
    return execute_query(
        "SELECT * FROM journal_entries WHERE user_id = %s ORDER BY entry_date DESC, created_at DESC",
        (user_id,),
        fetchall=True
    )

def get_journal_entry_by_id(user_id, entry_id):
    """Retrieve a single journal entry ensuring student ownership."""
    return execute_query(
        "SELECT * FROM journal_entries WHERE id = %s AND user_id = %s",
        (entry_id, user_id),
        fetchone=True
    )

def create_journal_entry(user_id, content):
    """
    Creates a private gratitude journal entry.
    Awards +15 points if this is the student's first entry created today.
    """
    today = date.today()
    content_clean = content.strip()
    if not content_clean:
        return False, "Journal entry cannot be empty."
        
    if len(content_clean) > 2000:
        return False, "Journal entry text exceeds maximum length of 2000 characters."

    # Check if entry already written today for point awarding
    existing_today = execute_query(
        "SELECT id FROM journal_entries WHERE user_id = %s AND entry_date = %s",
        (user_id, today),
        fetchone=True
    )

    entry_id = execute_query(
        "INSERT INTO journal_entries (user_id, entry_date, content, created_at) VALUES (%s, %s, %s, NOW())",
        (user_id, today, content_clean),
        commit=True
    )

    if not existing_today:
        add_user_points(user_id, POINTS_MAP['journal_entry'])
        
    check_and_award_achievements(user_id)
    return True, "Gratitude journal entry saved successfully!"

def update_journal_entry(user_id, entry_id, content):
    """Updates an existing journal entry with strict user ownership enforcement."""
    content_clean = content.strip()
    if not content_clean:
        return False, "Journal entry cannot be empty."
        
    rowcount = execute_query(
        "UPDATE journal_entries SET content = %s, updated_at = NOW() WHERE id = %s AND user_id = %s",
        (content_clean, entry_id, user_id),
        commit=True
    )
    if rowcount > 0:
        return True, "Journal entry updated successfully."
    return False, "Journal entry not found or access denied."

def delete_journal_entry(user_id, entry_id):
    """Deletes a journal entry with strict user ownership enforcement."""
    rowcount = execute_query(
        "DELETE FROM journal_entries WHERE id = %s AND user_id = %s",
        (entry_id, user_id),
        commit=True
    )
    if rowcount > 0:
        return True, "Journal entry deleted successfully."
    return False, "Journal entry not found or access denied."
