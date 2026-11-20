"""Oracle Always Free Ampere A1 makinesini kapasite açılana kadar dener ("Out of capacity" sorunu).

Her turda bölgedeki tüm erişilebilirlik alanlarında (AD) önce büyük şekli dener; `--kucuk-sonra` saat geçtikten
sonra küçük şekli de dener. Başarılı olunca genel IP'yi yazar ve çıkar. Ücretli kaynak açmaz: yalnız A1.Flex,
Always Free sınırları içinde (en çok 4 OCPU / 24 GB, 100 GB disk).

Kullanım (~/.oci/config hazır olmalı):
  python deploy/oracle/a1_dene.py --subnet <ocid> --image <ocid> --ssh ~/.ssh/id_ed25519.pub
"""
from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path

import oci


def log(msg: str) -> None:
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subnet", required=True)
    ap.add_argument("--image", required=True)
    ap.add_argument("--ssh", required=True)
    ap.add_argument("--ad", default="", help="virgüllü AD adları (boş = hepsi)")
    ap.add_argument("--ad-ad", default="citelex")
    ap.add_argument("--disk", type=int, default=100)
    ap.add_argument("--bekle", type=int, default=60, help="turlar arası saniye")
    ap.add_argument("--kucuk-sonra", type=float, default=3.0, help="kaç saat sonra 2 OCPU / 12 GB da denensin")
    ap.add_argument("--sonuc", default="a1_sonuc.txt")
    a = ap.parse_args()

    cfg = oci.config.from_file()
    tenancy = cfg["tenancy"]
    comp = oci.core.ComputeClient(cfg)
    net = oci.core.VirtualNetworkClient(cfg)
    ads = [x for x in a.ad.split(",") if x] or [
        d.name for d in oci.identity.IdentityClient(cfg).list_availability_domains(tenancy).data]
    ssh = Path(a.ssh).expanduser().read_text().strip()
    basla = time.time()
    tur = 0

    mevcut = [i for i in comp.list_instances(tenancy).data
              if i.display_name == a.ad_ad and i.lifecycle_state not in ("TERMINATED", "TERMINATING")]
    if mevcut:
        log(f"zaten var: {mevcut[0].id} ({mevcut[0].lifecycle_state}); çıkılıyor")
        return

    while True:
        tur += 1
        sekiller = [(4, 24)]
        if time.time() - basla > a.kucuk_sonra * 3600:
            sekiller.append((2, 12))
        for ocpu, gb in sekiller:
            for ad in ads:
                det = oci.core.models.LaunchInstanceDetails(
                    availability_domain=ad, compartment_id=tenancy, display_name=a.ad_ad,
                    shape="VM.Standard.A1.Flex",
                    shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(ocpus=ocpu, memory_in_gbs=gb),
                    source_details=oci.core.models.InstanceSourceViaImageDetails(
                        image_id=a.image, boot_volume_size_in_gbs=a.disk),
                    create_vnic_details=oci.core.models.CreateVnicDetails(subnet_id=a.subnet, assign_public_ip=True),
                    metadata={"ssh_authorized_keys": ssh})
                try:
                    inst = comp.launch_instance(det).data
                except oci.exceptions.ServiceError as e:
                    kisa = "kapasite yok" if "capacity" in (e.message or "").lower() else f"{e.status} {e.code}: {e.message}"
                    log(f"tur {tur} {ocpu}/{gb} {ad.split('-')[-1]}: {kisa}")
                    if e.status == 429:
                        time.sleep(30)
                    continue
                log(f"OLUŞTURULDU {ocpu} OCPU / {gb} GB, {ad}: {inst.id}")
                inst = oci.wait_until(comp, comp.get_instance(inst.id), "lifecycle_state", "RUNNING",
                                      max_wait_seconds=900).data
                vnic_id = comp.list_vnic_attachments(tenancy, instance_id=inst.id).data[0].vnic_id
                ip = net.get_vnic(vnic_id).data.public_ip
                Path(a.sonuc).write_text(f"{ip}\n{inst.id}\n{ocpu}/{gb}\n", encoding="utf-8")
                log(f"RUNNING, genel IP: {ip}")
                return
        time.sleep(a.bekle)


if __name__ == "__main__":
    main()
