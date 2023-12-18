'''
Created on 2023-06-19

@author: wf
'''
import sempubflow
class Version(object):
    """
    Version handling for SemanticPublishingFlow
    """
    name = "SemanticPublishingFlow"
    version = sempubflow.__version__
    date = '2023-06-19'
    updated = '2023-12-18'
    description = 'Semantic Publishing Workflow support'
    
    authors = 'Wolfgang Fahl'
    
    doc_url="https://github.com/WolfgangFahl/SemPubFlow"
    chat_url="https://github.com/WolfgangFahl/SemPubFlow/discussions"
    cm_url="https://github.com/WolfgangFahl/SemPubFlow"

    license = f'''Copyright 2023 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.'''
    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""