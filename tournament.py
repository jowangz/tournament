#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("connection error!")


def disconnect(db):
    """Commit and close database"""
    commit = db.commit()
    close = db.close()


def deleteMatches():
    """Remove all the match records from the database."""
    db, cursor = connect()
    # Delete all matches.
    players = cursor.execute("DELETE FROM matches;")
    disconnect(db)


def deletePlayers():
    """Remove all the player records from the database."""
    db, cursor = connect()
    # Delete all players.
    players = cursor.execute("DELETE FROM players;")
    disconnect(db)


def countPlayers():
    """Returns the number of players currently registered."""
    db, cursor = connect()
    # Count all players currently registered.
    cursor.execute("SELECT count(*) as num FROM players;")
    player_count = cursor.fetchone()[0]
    disconnect(db)
    return player_count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """

    db, cursor = connect()
    # Register a player with name.
    cursor.execute("INSERT INTO players (name) VALUES (%s)", (name,))
    disconnect(db)


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db, cursor = connect()
    # Return a list of tuples includes player_id, name, wins and number of
    # matches.
    cursor.execute("""
        SELECT * FROM player_standings_view;
        """)
    player_standing = cursor.fetchall()
    disconnect(db)
    return player_standing


def reportMatch(winner, loser, *draw):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    db, cursor = connect()
    # Check to see if this is a draw game.
    if draw:
        # Insert match result into Match table.
        cursor.execute("""
        INSERT INTO matches (player_1_id, player_2_id, winner)
        VALUES (%s, %s, %s)""", (winner, loser, -1))
        # Update winner matches count.
        cursor.execute("""
        UPDATE players
        SET matches_played = matches_played + 1,
        draw_encountered = draw_encountered + 1
        WHERE player_id = (%s)""", [winner])
        # Update loser matches count.
        cursor.execute("""
        UPDATE players
        SET matches_played = matches_played + 1,
        draw_encountered = draw_encountered + 1
        WHERE player_id = (%s)""", [loser])
        disconnect(db)
        return
    # Insert match result into Match table.
    cursor.execute("""
        INSERT INTO matches (player_1_id, player_2_id, winner)
        VALUES (%s, %s, %s)""", (winner, loser, winner))
    # Update winner matches count.
    cursor.execute("""
        UPDATE players
        SET matches_played = matches_played + 1
        WHERE player_id = (%s)""", [winner])
    # Update loser matches count.
    cursor.execute("""
        UPDATE players SET matches_played = matches_played + 1
        WHERE player_id = (%s)""", [loser])
    disconnect(db)


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # get player stadings.
    pairings = playerStandings()
    # check players count is an even number
    if len(pairings) % 2 == 0:
        # Extract id from pairings.
        player_id = [x[0] for x in pairings]
        # Extract name from pairings.
        player_name = [x[1] for x in pairings]
        # Reformat the list.
        pairings = zip(player_id, player_name)
        # Create an empty list.
        result = []
        for i in pairings:
            for j in i:
                result.append(j)
        # Return a list of tuples contains (id1, name1, id2, name2)
        it = iter(result)
        result = zip(it, it, it, it)
        return result
    else:
        print("We must have a even number of players")
