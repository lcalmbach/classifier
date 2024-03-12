info = ''''Diese App dient dazu,Thematische Stichwort-Bäume zu ertstellen und die unterste Ebene, Texten zuzuweisen. Der Workflow ist wie folgt:
1. Lade die Hierarchie der Stichworte hoch. Dies ist eine Datei mit den Spalten 
    - id: eine eindeutige Nummer
    - bezeichnung: Ein Stichwort
    - beschreibung: eine Beschreibung des Stichworts. Bei einzelnen Stichworten fehlt einem NLP algoritmus der Kontext. Deshalb ist es in gewissen Fällen sinnvoll, eine Beschreibung zu haben. z.B. kann das Stichwort "Wanderung" sowohl dem Theme Freizeit als auch dem Thema Bevölkerung zugeordnet werden. mit dem ergänzenden Text "Zuzüge Umzügen und Wegzüge er Bevlökerung" ist klar, dass es sich um das Thema Bevölkerung handelt.
    - ebene_id: ebene, in der das Stichwort erscheinen soll. Im Moment werden 3 Ebenen unterstützt.
    - vorgaenger_id: index des Vorgängers unter dem das Stichwort erscheinen soll. Diese Spalte wird durch die App gefüllt.
    - vorvorgaenger_id: Auf der Ebene 3 ist es oft sinnvoll, zuerst den Knoten auf Ebene 1 zu bestimmen (Grossmutter). die Unterschiede auf ieser Ebene sind oft recht gross und die Zuordnung einfach. Bei der zuordnung der Mutter-Ebene werden anschliessend nur noch Kinder des Grossmutterknotens berücksichtigt.

    als zweites Dokument kann eine Datei mit den Texten im csv Format hochgeladen werden. Dese Datei hat die Spalten:
    - id: eine eindeutige Nummer
    - text: ein Text
2. Wähle die Option "Hierarchie bilden". Hier kann die automatische Ordnung im Stichwortbaum ausgelöst werden.
3. Wähle die Option "Stichworte zuweisen". Hier können die Stichworte auf der untersten Ebene Texten zugeordnet werden. Die App bietet eine automatische Zuordnung an. Diese kann aber auch manuell angepasst werden.
4. Wähle die Option "Resultat editieren". Hier können die Ergebnisse bearbeitet und exportiert werden.
5. Zuweisung Stichwort zu Texten: Die App bietet eine automatische Zuordnung an. Diese kann aber auch manuell angepasst werden.

'''
info_tree_creation = '''
1. Weise Elemente der Ebene 2 der Ebene 1 zu
2. Weise Elemente der Ebene 1 der Ebene 3 zu. Dies erleichtert anschliessend die Zuweisung von Elementen der Ebene 3 zu Ebene 2, da die Auswahlmöglichkeiten von Ebene 2 eingeschränkt sind.
3. Weise elemente der Ebene 3 der Ebene 2 zu
4. Überprüfe den Baum
5. Wenn Stichworte falsch zugewiesen sind, so kann entweder in der Datei mit der Stichwort Hiearchie die Bezeichnung oder Beschreibung angepasst werden, oder die Zuweisung kann im einem nächsten Schritt manuell erfolgen. Achtung, im zweiten Fall gehen die Anpassungen verloren, wenn ein zweites Mal automatisch zugewiesen wird.
'''