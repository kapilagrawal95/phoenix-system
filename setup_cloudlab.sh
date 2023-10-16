#!/bin/bash
export IP=$(hostname -I | awk '{print $1}')
export SHARELATEX_REAL_TIME_URL_VALUE=$IP":30911" 
echo $SHARELATEX_REAL_TIME_URL_VALUE
export DOCSTORE_NODE=one
export DOCSTORE_CLAIMNAME=docstore-claim0
export FILESTORE_NODE=one
export FILESTORE_CLAIMNAME=filestore-claim0
export REDIS_NODE=one
export MONGO_NODE=four
export MONGO_CLAIMNAME=mongo-claim0
export WEB_NODE=one
export CONTACTS_NODE=two
export CONTACTS_CLAIMNAME=contacts-claim0
export CLSI_NODE=three
export DOCUMENT_UPDATER_NODE=four
export NOTIFICATIONS_NODE=two
export NOTIFICATIONS_CLAIMNAME=notifications-claim0
export REAL_TIME_NODE=three
export SPELLING_NODE=four
export SPELLING_CLAIMNAME=spelling-claim0
export TRACK_CHANGES_NODE=two
export TRACK_CHANGES_CLAIMNAME=track-changes-claim0
export CHAT_NODE=three
export TAGS_NODE=four
export TAGS_CLAIMNAME=tags-claim0
bash overleaf/launch.sh

# Note that pod to node ratio should be 10% to ensure less than 10 pods per node are scheduled.
