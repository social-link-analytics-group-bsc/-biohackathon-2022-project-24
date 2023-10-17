from lxml import etree
from utils.relevant_tags import value_sections


class XmlParser:
    def __init__(self, xml_document):
        if isinstance(xml_document, str) or isinstance(xml_document, bytes):
            # Parse the XML string into an Element object
            self.xml_document = etree.fromstring(xml_document)
        else:
            # If it's already an Element object, use it directly
            self.xml_document = xml_document

    def abstract(self):
        # Define the XPath expression to find abstract text with sections
        xpath_expression_with_sec = ".//front/abstract/sec"

        # Try to find the abstract element with sections
        abstract_elements = self.xml_document.findall(xpath_expression_with_sec)

        abstract_elements = [el.text for el in abstract_elements if el.text is not None]
        if abstract_elements:
            # If abstracts with sections are found, concatenate their text
            abstract_text = " ".join(
                abstract_element.strip() for abstract_element in abstract_elements
            )
            return abstract_text

        # If no abstracts with sections are found, try to find abstracts without sections
        xpath_expression_no_sec = ".//front/abstract"
        abstract_elements = self.xml_document.findall(xpath_expression_no_sec)

        abstract_elements = [el.text for el in abstract_elements if el.text is not None]
        if abstract_elements:
            # If abstracts without sections are found, concatenate their text
            abstract_text = " ".join(
                abstract_element.strip() for abstract_element in abstract_elements
            )
            return abstract_text

        # If no abstracts with sections are found, try to find abstracts without sections
        xpath_expression_no_sec = ".//front/abstract/p"
        abstract_elements = self.xml_document.findall(xpath_expression_no_sec)

        abstract_elements = [el.text for el in abstract_elements if el.text is not None]
        if abstract_elements:
            # If abstracts without sections are found, concatenate their text
            abstract_text = " ".join(
                abstract_element.strip() for abstract_element in abstract_elements
            )
            return abstract_text

    def article_type(self):
        article_type = self.xml_document.get("article-type")
        return article_type

    def article_title(self):
        title_xpath = ".//article-title"
        title_element = self.xml_document.find(title_xpath)
        title = title_element.text if title_element is not None else None
        return title

    def authors(self):
        author_xpath = ".//contrib[@contrib-type='author']"
        author_elements = self.xml_document.findall(author_xpath)
        authors = []
        for author_element in author_elements:
            name_element = author_element.find("name")
            if name_element is not None:
                surname = name_element.findtext("surname")
                given_names = name_element.findtext("given-names")
                authors.append(f"{given_names} {surname}")
        return authors

    def article_categories(self):
        categories_xpath = ".//article-categories/subj-group/subject"
        categories_elements = self.xml_document.findall(categories_xpath)
        if categories_elements is not None:
            categories = [el.text for el in categories_elements]
            return categories

    def journal_title(self):
        journal_title_xpath = ".//journal-title"
        journal_title_element = self.xml_document.find(journal_title_xpath)
        journal_title = (
            journal_title_element.text if journal_title_element is not None else None
        )
        return journal_title

    def publication_date(self):
        # FIXME change that one to match the publication date not the other one

        pub_date_xpath = ".//pub-date"
        pub_date_element = self.xml_document.find(pub_date_xpath)
        if pub_date_element is not None:
            year = pub_date_element.findtext("year")
            month = pub_date_element.findtext("month")
            day = pub_date_element.findtext("day")
            return {"year": year, "month": month, "day": day}

    def copyright_info(self):
        copyright_xpath = ".//permissions/copyright-statement"
        copyright_element = self.xml_document.find(copyright_xpath)
        if copyright_element is not None:
            copyright_ = copyright_element.text
            return copyright_

    def keywords(self):
        kwd_xpath = ".//kwd-group/kwd"
        kwd_elements = self.xml_document.findall(kwd_xpath)
        if kwd_elements is not None:
            return [el.text for el in kwd_elements]

    def ids(self):
        dict_ids = dict()
        pmcid_xpath = ".//article-id[@pub-id-type='pmcid']"
        publisher_id_xpath = ".//article-id[@pub-id-type='publisher-id']"
        doi_xpath = ".//article-id[@pub-id-type='doi']"
        pmcid_element = self.xml_document.find(pmcid_xpath)
        publisher_id_element = self.xml_document.find(publisher_id_xpath)
        doi_element = self.xml_document.find(doi_xpath)
        dict_ids["pmcid"] = pmcid_element.text if pmcid_element is not None else None
        dict_ids["publisher_id"] = (
            publisher_id_element.text if publisher_id_element is not None else None
        )
        dict_ids["doi"] = doi_element.text if doi_element is not None else None
        return dict_ids

    def funding(self):
        funding_xpath = ".//funding-source"
        funding_elements = self.xml_document.findall(funding_xpath)
        funding_info = []

        for funding_element in funding_elements:
            funding_dict = {}
            try:
                funding_dict["institution"] = funding_element.find(
                    ".//institution"
                ).text
            except AttributeError:
                pass
            try:
                funding_dict["award_id"] = funding_element.find(".//award-id").text
            except AttributeError:
                pass
            try:
                funding_dict["recipient_name"] = funding_element.find(
                    ".//principal-award-recipient/name"
                ).text
            except AttributeError:
                pass
            if funding_dict:
                funding_info.append(funding_dict)
        return funding_info

    def sections(self):
        dict_section = {k: None for k in value_sections}
        sections_xpath = ".//body/sec"
        sec_elements = self.xml_document.findall(sections_xpath)
        # Iterate through the sec elements
        for sec in sec_elements:
            sec_type = sec.attrib.get("sec-type", "").lower()
            # Check if the sec-type attribute matches any of the section fields
            for section in value_sections:
                for value in value_sections[section]:
                    if value in sec_type:
                        # Extract the text content of the section (text without tags)
                        section_text = "".join(sec.itertext())
                        dict_section[section] = section_text.replace('"', "'")
        if any(value is not None for value in dict_section.values()):
            return dict_section
        
        return None  # Return None if no sections match the criteria

class DynamicXmlParser(XmlParser):
    def __init__(self, xml_document):
        super().__init__(xml_document)
        self.data = {}  # Initialize a dictionary to store method results
        self.data_status = {}  # Initialize a dict to store the method status
        # Get the parents methods
        self.get_the_parents_methods()
        # Collect the results
        self.collect_results()
        # Populate the checking status
        self.check_methods()

    def get_the_parents_methods(self):

        self.parent_class_methods = [
            func
            for func in dir(XmlParser)
            if callable(getattr(XmlParser, func)) and not func.startswith("__")
        ]

    def collect_results(self):
        try:
            # Call each method and store the result in the data dictionary
            for method_name in self.parent_class_methods:
                method = getattr(self, method_name)
                try:
                    result = method()
                except Exception as e:
                    raise ValueError(
                        f"Method {method_name} failed with error: {str(e)}"
                    )
                self.data[method_name] = result
        except Exception as e:
            print(e)
            raise e


    def check_methods(self):
        # Check which methods returned False and create a dynamic dictionary
        for method_name in self.data:
            result = self.data[method_name]
            if result is None or (isinstance(result, (str, list)) and not result):
                self.data_status[method_name] = False
            else:
                if isinstance(result, dict):
                    for k in result:
                        if result[k] is not None:
                            self.data_status[k] = True
                        else:
                            self.data_status[k] = False
                else:
                    self.data_status[method_name] = True
